# -*- coding: utf-8 -*-
"""
Detect script but for video (both recorded and livestream)
Created on Tue Oct 12 12:18:53 2021

@author: salma

v5.1
Tom Zimmerman fixed a few bugs with counting the frames

v5.0
Background subtraction was implemented (for recorded video only!)

v4.0
A play bar was added to skip through the video (for recorded videos only). 

v3.1 
User can choose the csv filename and where they want to save it, 
but only creates one final file with the updated IDs

v3.0 
Some buttons were replaced with a scale (scrolling bar)

v2.0
Replaced the keyboard keys with mouse buttons (only works with recorded videos!)

v1.0
This script takes the livestream input of the microscope and returns the detect csv
file. The user can press 's' to start/pause saving objects in the livestream, and then
press 'q' to quit the program.
"""

import cv2
import numpy as np 
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

#################### CSV FILE NAME AND IMAGE RES ##############################
X_REZ=640; Y_REZ=480;               # viewing resolution
THICK=1                             # bounding box line thickness 
BLUR=7                              # object bluring to help detection
VGA=(X_REZ,Y_REZ)
PROCESS_REZ=(X_REZ//2,Y_REZ//2)
    
############################ DEFINE VARIABLES ################################
detectHeader= 'FRAME,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE' 
FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; AREA=8; AR=9; ANGLE=10; MAX_COL=11 # pointers to detection features
detectArray=np.empty((0,MAX_COL))  # detection features populated with object for each frame

#variables associated with buttons (originally with keystrokes) and the starting values
thresh = 60
MIN_AREA = 50
MAX_AREA = 1500
save = 0        # saves the objects detected to the csv file
play = True     # plays the video (or lets the livestream run)
back_sub = False
GOOD_VIDEO=0    # set if video file or stream is opened
EXIT_BUTTON=0   # set when EXIT button pressed to end program
########################## DEFINING FUNCTIONS IN ORDER ############################

#get median frame as background
def getMedian(vid,medianFrames,TINY_REZ):
    # Open Video
    print ('openVideo:',vid)
    cap = cv2.VideoCapture(vid)
    #cap.set(3, 1280); cap.set(4, 720);  # set to 720p resolution (1920,1080 for 1080p)
    maxFrame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1
    print('maxFrame',maxFrame) 
     
    # Randomly select N frames
    skipFrames = 50
    print('calculating median for background subtraction...')
    #frameIds = skipFrames + (maxFrame-skipFrames) * np.random.uniform(size=medianFrames)
    frameIds = np.random.randint(skipFrames,maxFrame,medianFrames)
    #print('Frame ID list',frameIds)
    frames = [] # Store selected frames in an array
    for fid in frameIds:
        #cap.set(cv2.CAP_PROP_POS_FRAMES, fid//1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
        ret, frame = cap.read()                           # some frames can't be read for some reason
        colorIM=cv2.resize(frame,TINY_REZ)
        grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)
        frames.append(grayIM)
        
    medianFrame = np.median(frames, axis=0).astype(dtype=np.uint8)     # Calculate the median along the time axis
    cap.release()
    return medianFrame


#get objects (contouring)
def getAR(obj):
    ((xc,yc),(w,h),(angle)) = cv2.minAreaRect(obj)  # get parameters from min area rectangle
    ar=0.0      # initialize aspect ratio as a floating point so calculations are done in floating point
    # calculate aspect ratio (always 1 or greater)
    if w>=h and h>0:
        ar=w/h
    elif w>0:
        ar=h/w
    return(xc,yc,ar,angle)

def opening_video(): # function to open video
    global GOOD_VIDEO
    
    GOOD_VIDEO=0                       # set if video file or livestream open
    fileName='dummy'                            # give dummy name in case using live streaming
    if vid_type == 'STREAM':                     # if user chooses livestream
        try:
            cap = cv2.VideoCapture(0)           # start livestream (will set it to be 1 for microscope) 
            GOOD_VIDEO=1
        except:
            GOOD_VIDEO=0
            
    elif vid_type == 'FILE':                   # if user chooses a recorded video
        file_man = tk.Tk()
        file_man.title('FM1')
        file_man.withdraw()
        file = filedialog.askopenfilename(filetypes = [('all files','*.*')])
        fileName = file.split('/')
        fileName = fileName[-1]
        try:
            cap = cv2.VideoCapture(file)
            medianFrame = getMedian(file,25,PROCESS_REZ)
            GOOD_VIDEO=1
        except AttributeError:
            print('Must be an mp4/video file')
            print()
            GOOD_VIDEO=0
    
    return(cap,GOOD_VIDEO,medianFrame,fileName)


def frame_processing(): # function to process a single frame
    global detectArray, colorIM, binaryIM, frame_slider, frameCount, medianFrame, vid_type, GOOD_VIDEO, play
    
    #calls a single frame
    cap.set(1, frame_slider)
    ret, testIM = cap.read()             # a single frame
    
    if ret==0:
        #GOOD_VIDEO=0   if you want to end program when playing video is done
        #return
        frame_slider=0
        cap.set(1, frame_slider)
        ret, testIM = cap.read()             # read a single frame
        play=False                         # stop play
        #SALMA add code here to unpress the play button!            
        
    
    # blur and threshold image
    colorIM=cv2.resize(testIM,PROCESS_REZ)
    grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)  # convert color to grayscale image    
    
    if vid_type == 'FILE':
        diffIM = cv2.absdiff(grayIM, medianFrame)   # Calculate absolute difference of current frame and the median frame 
        if back_sub: #if background subtraction is on
            blurIM = cv2.blur(diffIM,(BLUR,BLUR))
            ret,binaryIM = cv2.threshold(blurIM,thresh,255,cv2.THRESH_BINARY) # threshold image to make pixels 0 or 255
        else:
            blurIM = cv2.medianBlur(grayIM,BLUR)                  # blur image to fill in holes to make solid object
            diffIM = grayIM       # so that the display window stays open but without the background subtraction
            ret,binaryIM = cv2.threshold(blurIM,thresh,255,cv2.THRESH_BINARY_INV) # threshold image to make pixels 0 or 255
            
    elif vid_type == 'STREAM':
        blurIM = cv2.medianBlur(grayIM,BLUR)                  # blur image to fill in holes to make solid object
        diffIM = grayIM       # so that the display window stays open but without the background subtraction
        ret,binaryIM = cv2.threshold(blurIM,thresh,255,cv2.THRESH_BINARY_INV) # threshold image to make pixels 0 or 255
    
    # get contours  # dummy, 
    contourList, hierarchy = cv2.findContours(binaryIM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # all countour points, uses more memory
    
    # draw bounding boxes around objects
    objCount=0                                      # used as object ID in detectArray
    for objContour in contourList:                  # process all objects in the contourList
        area = int(cv2.contourArea(objContour))     # find obj area        
        if MAX_AREA > area >MIN_AREA:                           # only detect large objects       
            PO = cv2.boundingRect(objContour)
            x0=PO[0]; y0=PO[1]; x1=x0+PO[2]; y1=y0+PO[3]
            cv2.rectangle(colorIM, (x0,y0), (x1,y1), (0,255,0), THICK) # place GREEN rectangle around each object, BGR
            (xc,yc,ar,angle)=getAR(objContour)
            if play and save: 
                # save object parameters in detectArray in format FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; CLASS=8; AREA=9; AR=10; ANGLE=11; MAX_COL=12
                parm = np.array([[frameCount,objCount,x0,y0,x1,y1,xc,yc,area,ar,angle]]) # create parameter vector (1 x MAX_COL) 
                detectArray=np.append(detectArray,parm,axis=0) 
                objCount+=1                                     # indicate processed an object
    
    # shows results
    cv2.imshow('colorIM', cv2.resize(colorIM,VGA))      # display image
    #cv2.imshow('blurIM', cv2.resize(blurIM,VGA))       # display blurred image
    cv2.imshow('binaryIM', cv2.resize(binaryIM,VGA))    # display thresh image
    cv2.imshow('diffIM', cv2.resize(diffIM,VGA))        # display thresh image
    cv2.waitKey(1)
    
    if play:
        frame_slider += 1
        if save:
            frameCount +=1
    return       

def dist(point1, point2, point3, point4): #to find distance between objects
    x1 = float(point1)
    y1 = float(point2)
    x2 = float(point3)
    y2 = float(point4)
    arg = (x2 - x1)**2 + (y2 - y1)**2
    dist = arg**0.5
    return dist

def updateStatusDisplay(): #what goes on the status bar on top of the screen
    global root,thresh,MIN_AREA,MAX_AREA, frame_slider, big_label
    thresh = int(slide_var1.get())
    MIN_AREA = int(slide_var2.get())
    MAX_AREA = int(slide_var3.get())
    frame_slider = int(slide_var4.get())
    if vid_type == 'STREAM':
        textOut='   Video name= Livestream        Threshold=' + str(thresh) + '    Min Area=' + str(MIN_AREA) + '    Max Area=' + str(MAX_AREA)
    else:
        textOut='   Video name=' + str(fileName)+'       Threshold=' + str(thresh) + '    Min Area=' + str(MIN_AREA) + '    Max Area=' + str(MAX_AREA)+ '   Frame Number: ' + str(frame_slider)
    big_label = tk.Label(root, text=textOut,bg="cyan",justify = tk.LEFT).grid(row=0,column=0,columnspan=5)

def play_bar(event): # play bar function (so the user can skip through the video)
    global frame_slider,frameCount
    frame_slider = int(slide_var4.get()) 
    frameCount = frame_slider

def doButton(): #determines functions of each button
    global thresh, MIN_AREA, MAX_AREA, skip_im, save, EXIT_BUTTON, play, back_sub
   
    val=v.get()
    but=names[val]

    if 'Stop Detecting' in but:
        save = 0
        title4['text'] = 'Stopped Detection'
        #print('save is:',save,'play is:',play, 'EXIT_BUTTON is:',EXIT_BUTTON)
        
    elif 'Start Detecting' in but:
        #print('Started Detection')
        save = 1        # this flag saves the objects to the csv file
        title4['text'] = 'Started Detection'
        #print('save is:',save,'play is:',play, 'EXIT_BUTTON is:',EXIT_BUTTON)
    
    if "Play/pause video" in but:
        play = not play
        if play is False:
            title4['text'] = 'Video is paused'
        else:
            title4['text'] = ' '
        
    elif 'Exit' in but:
        EXIT_BUTTON = 1             # quits livestream
        #cap.release()
        #cv2.destroyAllWindows()
        #root.withdraw()
        return
    
    updateStatusDisplay()
    frame_processing()      # detect script (single frame)
    return

def scrolling(event): #function for scrolling
    updateStatusDisplay()
    frame_processing()
    return

def back_sub_button():
    global back_sub, title4
    back_sub = not back_sub
    if back_sub is True:
        title4['text'] = 'Background Subtraction is enabled'
    else:
        title4['text'] = 'Background Subtraction is disabled'
    return

def save_file(): #function to have user save the csv with the desired filename
    global detectFileName, root
    root = tk.Tk()
    root.title('FM2')
    root.withdraw()
    detectFileName=filedialog.asksaveasfilename(filetypes = [('comma-separated values (CSV)','.csv'), ('text file','.txt')], 
                                                defaultextension = '.csv')
    root.destroy()
    return

def livestream_question(): #creates a widget that asks the user which video type they want
    global answer, welcome_message
    question= tk.Tk()
    question.title('Choose a Video Format')
    #question.geometry('300x200')
    wel_label = tk.Label(question,text=welcome_message, justify = 'left')
    label = tk.Label(question,text='Choose the video type to detect objects')
    
    answer = ''             # answer if the user wants to use the livestream or not
    
    def live_answer():
        global answer
        answer = 'STREAM'
        question.withdraw()
        return
    
    def rec_answer():
        global answer
        answer = 'FILE'
        question.withdraw()
        return
    
    #making the buttons
    livestream = tk.Button(question, text = 'Livestream', command = live_answer,
                           width = 50, activebackground = 'cyan')
    recorded = tk.Button(question,text = 'Recorded Video', command = rec_answer,
                         width = 50, activebackground = 'cyan')
    
    wel_label.pack()
    label.pack()
    livestream.pack()
    recorded.pack()
    
    while answer == '':
        question.update_idletasks()
        question.update()
        
    return answer

############################# GLOBAL VAR FOR MOUSE ###########################
BUTTON_WIDTH=20         # button display width
WINDOW_SCALE=10         # window size increment
FULL_SCALE=2            # reduce full scale image by this factor so it fits in window

def doc():
    print()
    print('============================ USER GUIDE ==============================')
    print('Use Min Area to adjust the minimum area for detection')
    print('Use Max Area to adjust the maximum area for detection')
    print('Use Threshold to adjust the pixel threshold for detection')
    print('Click "Start Detecting" to save the objects detected into the csv file')
    print('Click "Stop Detecting" to stop saving the objects detected into the csv file')
    print('Click "Exit" to end program')
    print('======================================================================')
    print()

# Button names. Some are left blank for future functions.
names = [
    ("Play/pause video"),
    ("Start Detecting"),
    ("Stop Detecting"),
    ("Exit"), 
]

# welcome message when you first run the program
welcome_message = '''
                                                          MICROSCOPE UI
                            Author: Salma Ahmed         CHEM 667        Fall 2021

Welcome! This GUI uses the detect program (created by Tom Zimmerman) to detect 
objects in a video, whether it be a livestream or a recorded video.

When using this program, please use the "Exit" Buttons to close it, DO NOT
use the red "X" on top of the window

2022 UPDATE: This program now includes background subtraction for recorded videos!
'''

##################################### MAIN #####################################

doc() #to print the user guide

# Asks user if they are running a recording video or a livestream
vid_type = livestream_question()   
 
frame_slider = 0                         # keeps track of frame number (in video)
frameCount=0                        # keeps track of frame number (in csv)
cap,GOOD_VIDEO,medianFrame,fileName=opening_video() # opens video

player_style = ttk.Style()
player_style.configure('Horizontal.TScale', activebackground = 'orange') # give play bar a different color

if GOOD_VIDEO:
    root = tk.Toplevel()      # root is for button / slider grid
    v = tk.IntVar()
    v.set(1)
    slide_var1 = tk.DoubleVar()
    slide_var2 = tk.DoubleVar()
    slide_var3 = tk.DoubleVar()
    slide_var4 = tk.DoubleVar()
    
    root.title("Detection Functions")
    
    # gets the total number of frames in the video
    vid_length= int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_length= int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-1
    print('total frames:',vid_length)
    
    # Here are the sliders
    
    #threshold slider
    slider = ttk.Scale(root, from_=0, to=255, orient='horizontal', 
                       length = 500,variable=slide_var1,command=scrolling) #threshold
    slider.grid(row=1,column= 1)
    slider.set(60)
    title1 = tk.Label(root, text = 'Threshold').grid(row = 1, column =0)

    #minimum area slider
    slider_2 = ttk.Scale(root, from_=0, to=2000, orient='horizontal', 
                        length = 500,variable=slide_var2,command=scrolling) #min area
    slider_2.grid(row=2,column= 1)
    slider_2.set(50)
    title2 = tk.Label(root, text = 'Minimum Area').grid(row = 2, column = 0)
    
    #maximum area slider
    slider_3 = ttk.Scale(root, from_=0, to=3000, orient='horizontal', 
                        length = 500,variable=slide_var3,command=scrolling) #max area
    slider_3.grid(row=3,column= 1)
    slider_3.set(1500)
    title3 = tk.Label(root, text = 'Maximum Area').grid(row = 3, column = 0)
    
    #play bar slider
    slider_4 = ttk.Scale(root, from_=0, to=vid_length, orient = 'horizontal', 
                       length = 500,variable=slide_var4, style= 'Horizontal.TScale',
                       command=play_bar)
    slider_4.grid(row=4, column = 1)
    slider_4.set(frame_slider)
    title5 = tk.Label(root, text = 'Video Progress')
    title5.grid(row = 4, column = 0)
    if vid_type == 'STREAM':
        slider_4['state'] = 'disabled'
        title5.configure(text = 'Video Progress (disabled)')
    
    # Here are the buttons
    for val, txt in enumerate(names): #goes through each button (and what they'd look like)
        r=int(5+val/5)
        c=int(val%5)
        if vid_type == 'STREAM' and txt == 'Play/pause video': # disables play button if the video is livestream
            tk.Radiobutton(root, text=txt + str('(Disabled)'),padx = 1, variable=v,width=BUTTON_WIDTH,
                           command=doButton,indicatoron=True,value=val,
                           state = 'disabled').grid(row=r,column=c)
            play = True
        else:
            tk.Radiobutton(root, text=txt,padx = 1, variable=v,width=BUTTON_WIDTH,
                           command=doButton,indicatoron=True,value=val,
                           activebackground = 'cyan').grid(row=r,column=c)
    
    
    #label below the buttons
    if vid_type == 'FILE': #this means that a recorded video is playing
        title4 = tk.Label(root, text = 'Press "play/pause" to play video')
        play = False
        
        #background subtraction checkbox
        back_sub_checkbox = ttk.Checkbutton(root, text = 'Background sub',
                                            command = back_sub_button)
        back_sub_checkbox.grid(row = 6, column = 0)

    else: # this means that the livestream is running
        title4 = tk.Label(root, text = 'Livestream is running')
    title4.grid(row=6, column = 1)
    
    updateStatusDisplay() # status display


    while GOOD_VIDEO==1 and EXIT_BUTTON==0: # while loop that goes through each frame
        frame_processing()          # detect script of a single frame, sets GOOD_VIDEO=0 when no more frames to read
        if vid_type == 'FILE':
            slide_var4.set(frame_slider)     # update the slider to be current frame value
            textOut='   Video name=' + str(fileName)+'       Threshold=' + str(thresh) + '    Min Area=' + str(MIN_AREA) + '    Max Area=' + str(MAX_AREA)+ '   Frame Number: ' + str(int(slide_var4.get()))
            big_label = tk.Label(root, text=textOut,bg="cyan",justify = tk.LEFT).grid(row=0,column=0,columnspan=5)
        root.update()
 
    GOOD_VIDEO=0 # end video processing

# end video processing
cap.release()
root.withdraw()
cv2.destroyAllWindows()             # clean up to end program
print('Video closed, windows destroyed, UI stopped')
print('Done with video. Saving raw feature file and exiting program')


################ tracking the objects to update their IDs ######################
print(' ')
print('Processing Object IDs ...')
data = detectArray              # to keep variables from HW 6

# code from Homework 6
framed_data = np.unique(data[:,FRAME])
all_x_data = data[:,XC]
all_y_data = data[:,YC]
all_IDs = data[:,ID]
distByFrame = []
#ind_counter = np.where(data[:,FRAME] == 1)[0][0]
ind_counter = 0
print('Frame Slider:',frame_slider)
maxFrames=len(framed_data)   
print('Total frames saved:',maxFrames) 
#for i in range(10): #to test loop
for i in range(maxFrames-1): ## frames count from 0, so 100 frames goes from 0 to 99, hence -1
    obj_data = np.where(data[:,FRAME] == i) #current frame index
    obj_next_data = np.where(data[:,FRAME] == i + 1) #next frame index
    for item in range(len(obj_data)):
        IDs_frame1 = all_IDs[obj_data[item]]
        IDs_frame2 = all_IDs[obj_data[item]]
        X_frame1 = all_x_data[obj_data[item]] #all X's in frame i
        Y_frame1 = all_y_data[obj_data[item]] #all Y's in frame i
        X_frame2 = all_x_data[obj_next_data[item]] #all X's in frame i + 1
        Y_frame2 = all_y_data[obj_next_data[item]] #all Y's in frame i + 1
        for j in range(len(X_frame1)): #for each x value in frame i
            if not (i == 0 and j == 0): #so the counter starts at 0 for the 0th frame, 0th object
                ind_counter += 1
            X1 = X_frame1[j]
            Y1 = Y_frame1[j]
            dist_dict = {}
            for p in range(len(X_frame2)): #for each x value in frame i + 1
                X2 = X_frame2[p]
                Y2 = Y_frame2[p]
                distance = dist(X1,Y1,X2,Y2)
                dist_dict[p] = distance #assigns each object with a distance
                
            #here I need to sort out the dictionary by values (i.e. by distance)
            dist_list = sorted(dist_dict.items(), key = lambda x:x[1])
            
            #here is the where I updated the ID number
            data[ind_counter,ID] = dist_list[0][0] #the object associated with the shortest distance

#creating the new csv file
save_file()
try:
    np.savetxt(detectFileName, data, fmt= '%d', header = detectHeader, delimiter = ',')
    print(' ')
    print('File with updated IDs was created successfully!')
    
except FileNotFoundError:
    print('No file name input, CSV file was not saved...')
      
print('bye!')               # tell the user program has ended

