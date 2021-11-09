# -*- coding: utf-8 -*-
"""
Detect script but for images
Created on Tue Oct 12 12:18:53 2021

@author: salma

v2.0
Replaced the keyboard keys with mouse buttons

v1.0
This script takes the livestream input of the microscope and returns the detect csv
file. The user can press 's' to start/pause saving objects in the livestream, and then
press 'q' to quit the program.
"""
import cv2
import numpy as np
import tkinter as tk
import warnings

warnings.filterwarnings('ignore')
#################### CSV FILE NAME AND IMAGE RES ##############################
detectFileName='detection_mouselivestream_updatedID.csv'      # output file containing object location, area, aspect ratio for each piceo frame
temp_name = 'raw_mouselivestream_detection.csv'
X_REZ=640; Y_REZ=480;               # viewing resolution
THICK=1                             # bounding box line thickness
BLUR=7                              # object bluring to help detection
VGA=(X_REZ,Y_REZ)
PROCESS_REZ=(X_REZ//2,Y_REZ//2)
    
############################ DEFINE VARIABLES ################################
detectHeader= 'FRAME,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE' 
#detectHeader= detectHeader.split(',')
#print(detectHeader)
FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; AREA=8; AR=9; ANGLE=10; MAX_COL=11 # pointers to detection features
detectArray=np.empty((0,MAX_COL))  # detection features populated with object for each frame
#detectList = []

#variables associated with buttons (originally with keystrokes) and the starting values
thresh = 60
MIN_AREA = 50
MAX_AREA = 2000
run = 1         # runs program until user clicks "Exit"
save = 0        # saves the objects detected to the csv file

########################## DEFINING FUNCTIONS IN ORDER ############################

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
    global cap
    #cap = cv2.VideoCapture(1)           # start video file reader (currently livestream)
    cap = cv2.VideoCapture('fiveSecondPlankton.mp4')
    cap.set(3, 1920); cap.set(4, 1080);  # set to 1080p resolution
    return

def frame_processing(): # function to process a single frame
    global detectArray
    frameCount=0                        # keeps track of frame number
    while(cap.isOpened() and run):    # process each frame until end of video or 'q' key is pressed
    
        # get image
        ret, vid_frame = cap.read()
        if not ret:                     # check to make sure there was a frame to read
            print('Can not find video or we are all done')
            #break
        #print('original size:',colorIM.shape)
        
        # blur and threshold image
        colorIM=cv2.resize(vid_frame,PROCESS_REZ)
        grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)  # convert color to grayscale image       
        blurIM=cv2.medianBlur(grayIM,BLUR)                  # blur image to fill in holes to make solid object
        ret,binaryIM = cv2.threshold(blurIM,thresh,255,cv2.THRESH_BINARY_INV) # threshold image to make pixels 0 or 255
        
        # get contours  # dummy, 
        contourList, hierarchy = cv2.findContours(binaryIM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # all countour points, uses more memory
        
        # draw bounding boxes around objects
        objCount=0                                      # used as object ID in detectArray
        for objContour in contourList:                  # process all objects in the contourList
            area = int(cv2.contourArea(objContour))     # find obj area        
            if area>MIN_AREA:                           # only detect large objects       
                PO = cv2.boundingRect(objContour)
                x0=PO[0]; y0=PO[1]; x1=x0+PO[2]; y1=y0+PO[3]
                cv2.rectangle(colorIM, (x0,y0), (x1,y1), (0,255,0), THICK) # place GREEN rectangle around each object, BGR
                (xc,yc,ar,angle)=getAR(objContour)
                if save: 
                    #frameCount+=1 #start frame count here
                    # save object parameters in detectArray in format FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; CLASS=8; AREA=9; AR=10; ANGLE=11; MAX_COL=12
                    parm = np.array([[frameCount,objCount,x0,y0,x1,y1,xc,yc,area,ar,angle]]) # create parameter vector (1 x MAX_COL) 
                    detectArray=np.append(detectArray,parm,axis=0) 
                    print('Object #',objCount,'saved!')
                    objCount+=1                                     # indicate processed an object
                    
        #print('frame:',frameCount,'objects:',len(contourList),'big objects:',objCount)
    
        # shows results
        cv2.imshow('colorIM', cv2.resize(colorIM,VGA))      # display image
        #cv2.imshow('blurIM', cv2.resize(blurIM,VGA)) # display blurred image
        cv2.imshow('binaryIM', cv2.resize(binaryIM,VGA))# display thresh image
        if save:
            frameCount+=1
        #cv2.waitKey(0) #waits for user to close windows
        return

#the main detection script (now split into two functions)
def mainDetection():
    opening_video()
    frame_processing()
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
    global root
    textOut='   Video name= Livestream        Threshold=' + str(thresh) + '    Min Area=' + str(MIN_AREA) + '    Max Area=' + str(MAX_AREA)+'   '
    tk.Label(root, text=textOut,bg="cyan",justify = tk.LEFT).grid(row=0,column=0,columnspan=4)
    

def doButton(): #determines functions of each button
    #global frameCount,displayScale,Z,CROP,getCenter,savePic,bkgState,bkgIM
    global thresh, MIN_AREA, MAX_AREA, skip_im, save, run
   
    val=v.get()
    but=names[val] 
    #print('But:',but,'Val:', val)

    increment=0
    if "-10" in but:
        increment=-10
    elif "+10" in but:
        increment=10
    elif "-1" in but:
        increment=-1
    elif "+1" in but:
        increment=1

    if 'Stop Detecting' in but:
        print('Stopped Detection')
        save = 0
        
    elif 'Start Detecting' in but:
        print('Started Detection')
        save = 1        # this flag saves the objects to the csv file
        
    elif 'Min Area' in but:
        MIN_AREA+=increment
        if MIN_AREA < 0: #so we don't get negative values
            MIN_AREA = 0
        
    elif 'Max Area' in but:
        MAX_AREA+=increment
        if MAX_AREA < 0: #so we don't get negative values
            MAX_AREA = 0

    elif 'Threshold' in but:
        thresh+=increment
        if thresh < 0: #so we don't get negative values
            thresh = 0
    
    elif 'Exit' in but:
        run = 0         #quits livestream
        root.withdraw()
        root.destroy()
        cv2.destroyAllWindows()
        return
    
    updateStatusDisplay()
    frame_processing() #detect script
    return

######################### creating the button display ########################
def doMouse(event,x,y,flags,param): # don't really need this?
    global xc,yc
    
    if event == cv2.EVENT_LBUTTONDOWN:
        #xc,yc = x*FULL_SCALE,y*FULL_SCALE # compensate for full scale scaling
        frame_processing()
    return 

def auto_callback(): # the "demon" function that allows the script to run 
    while run: 
        frame_processing()
        root.after(30) #go to the next frame after 30 ms (since the video is 30 fps)
    return

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
    ("Min Area -10"),
    ("Min Area -1"),
    ("Min Area +1"),
    ("Min Area +10"),
    ("Max Area -10"),
    ("Max Area -1"),
    ("Max Area +1"),
    ("Max Area +10"),
    ("Threshold -10"),
    ("Threshold -1"),
    ("Threshold +1"),
    ("Threshold +10"),
    (" "), 
    ("Start Detecting"),
    ("Stop Detecting"),
    ("Exit"), 
    (" "), 
    (" "),
    (" "),
    (" ")
]

##################################### MAIN #####################################

doc() #to print the user guide

# TO DO LIST:
#set up open video code and separate the code that detects each frame (lines 66 - 111)
#take detect_livestream_SA and split it into two
#create a callback function that calls every 30 fps (check by printing the frame number)

#root is for button grid
root = tk.Tk() 
v = tk.IntVar()

root.title("Detection Functions")
updateStatusDisplay()

for val, txt in enumerate(names): #goes through each button (and what they'd look like)
    r=int(1+val/4)
    c=int(val%4)
    tk.Radiobutton(root, text=txt,padx = 1, variable=v,width=BUTTON_WIDTH,command=doButton,indicatoron=0,value=val).grid(row=r,column=c)

#cap = cv2.VideoCapture(1)           # start video file reader (currently livestream)

#cv2.setMouseCallback('Full Image',doMouse)
#cv2.setMouseCallback('Demon function',auto_callback)

#mainDetection()
opening_video()
frame_processing()
print('End of loop')
root.mainloop()     # program will keep waiting until a button has been pressed

cv2.destroyAllWindows()             # clean up to end program
cap.release()
print('video closed')

#saves data into the csv file
print('Done with livestream. Saving raw feature file and exiting program')
np.savetxt(temp_name,detectArray,header=detectHeader,delimiter=',', fmt = '%d') # original csv

################ tracking the objects to update their IDs ######################
print(' ')
print('Processing Object IDs ...')
data = detectArray              # to keep variables from HW 6

# code from Homework 6
framed_data = np.unique(data[:,FRAME])
all_x_data = data[:,XC]
all_y_data = data[:,YC]
distByFrame = []
ind_counter = 0
maxFrames=len(np.unique(data[:,FRAME]))
print('Total frames',maxFrames)
#for i in range(10): #to test loop
for i in range(maxFrames-1): #to prevent frames from being repeated
    obj_data = np.where(data[:,FRAME] == i) #current frame index
    obj_next_data = np.where(data[:,FRAME] == i + 1) #next frame index
    for item in range(len(obj_data)):
        first_ref = data[obj_data[item],ID]
        second_ref = data[obj_next_data[item],ID]
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
np.savetxt(detectFileName, data, fmt= '%d', header = detectHeader, delimiter = ',')
print(' ')
print('File with updated IDs was created successfully!')
print('bye!')               # tell the user program has ended

