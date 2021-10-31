# -*- coding: utf-8 -*-
"""
Detect script but for images
Created on Tue Oct 12 12:18:53 2021

@author: salma

v3.0
Replaced the keyboard keys with mouse buttons

v2.0
The keyboard module was added to adjust parameters. Keys such as 'n' and 's' were
added in order to go to the next image and save the object parameters respectively.
This also includes the image name in the csv file

v1.0
This script should detect objects for an image. In the future, it might be a module
added to the final detect script?
"""
import cv2
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import warnings

warnings.filterwarnings('ignore')
#################### CSV FILE NAME AND IMAGE RES ##############################
detectFileName='detection_image_mouse.csv'      # output file containing object location, area, aspect ratio for each piceo frame
X_REZ=640; Y_REZ=480;               # viewing resolution
THICK=1                             # bounding box line thickness
BLUR=7                              # object bluring to help detection
VGA=(640,480)
PROCESS_REZ=(320,240)
window=[0,Y_REZ,0,X_REZ]
    
############################ DEFINE VARIABLES ################################
detectHeader= 'IMAGE_NAME,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE'
detectHeader= detectHeader.split(',')
#print(detectHeader)
FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; AREA=8; AR=9; ANGLE=10; MAX_COL=11 # pointers to detection features
#detectArray=np.empty((0,MAX_COL))  # detection features populated with object for each frame
detectList = []

#variables associated with buttons (originally with keystrokes) and the starting values
thresh = 50
MIN_AREA = 50
MAX_AREA = 2000
skip_im = 1     # goes to the next image (the word "next" is already a keyword)
save = 0        # saves the objects detected to the csv file

########################## DEFINING FUNCTIONS IN ORDER ############################
def getImage():
    global root, file
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename() #the file you choose is in the form of the pathway string
    #file = 'black_mountain.jpg'
    print('File chosen:',file)
    try:
        image = cv2.imread(file)
        return image
    except AttributeError:
        return 'Must be a jpg or a png!'

#function to name image (for 1st column in the csv file)
def csv_image_name(filename):
    filename = filename[:-4]
    split_file = filename.split('/')
    return split_file[-1]

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

#the main detection script
def mainDetection():
    frameCount=0                        # keeps track of image number
    
    # blur and threshold image
    #pic = getImage()
    #global pic, thresh
    colorIM=cv2.resize(pic,PROCESS_REZ)
    grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)  # convert color to grayscale image       
    blurIM=cv2.medianBlur(grayIM,BLUR)                  # blur image to fill in holes to make solid object
    ret,binaryIM = cv2.threshold(blurIM,thresh,255,cv2.THRESH_BINARY_INV) # threshold image to make pixels 0 or 255
    
    # get contours  # dummy, 
    contourList, hierarchy = cv2.findContours(binaryIM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # all countour points, uses more memory
    
    # draw bounding boxes around objects
    global objCount, save, MIN_AREA, MAX_AREA, x0,y0,x1,y1,xc,yc,ar,angle, area
    objCount=0                                      # used as object ID in detectArray
    for objContour in contourList:  # process all objects in the contourList                
        area = int(cv2.contourArea(objContour))     # find obj area        
        if MAX_AREA > area > MIN_AREA:                           # only detect large objects       
            PO = cv2.boundingRect(objContour)
            x0=PO[0]; y0=PO[1]; x1=x0+PO[2]; y1=y0+PO[3]
            cv2.rectangle(colorIM, (x0,y0), (x1,y1), (0,255,0), THICK) # place GREEN rectangle around each object, BGR
            (xc,yc,ar,angle)=getAR(objContour)
            objCount+=1                                     # indicate processed an object
            
            # save object parameters in detectArray in format FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; CLASS=8; AREA=9; AR=10; ANGLE=11; MAX_COL=12
            if save:
                parm = [csv_image_name(file),objCount,x0,y0,x1,y1,xc,yc,area,ar,angle] # create parameter vector (1 x MAX_COL) 
                detectList.append(parm)
                print('Objects Saved!')
    save = 0
    # shows results
    cv2.imshow('colorIM', cv2.resize(colorIM,VGA))      # display image
    #cv2.imshow('blurIM', cv2.resize(blurIM,VGA)) # display thresh image
    cv2.imshow('binaryIM', cv2.resize(binaryIM,VGA))# display thresh image
    
    frameCount+=1
    return         

def updateStatusDisplay(): #what goes on the status bar on top of the screen
    global root_2
    textOut='   Image name='+ str(csv_image_name(file)) + '    Threshold=' + str(thresh) + '    Min Area=' + str(MIN_AREA) + '    Max Area=' + str(MAX_AREA)+'   '
    tk.Label(root_2, text=textOut,bg="pink",justify = tk.LEFT).grid(row=0,column=0,columnspan=4)
    

def doButton(): #determines functions of each button
    #global frameCount,displayScale,Z,CROP,getCenter,savePic,bkgState,bkgIM
    global thresh, MIN_AREA, MAX_AREA, skip_im, save
   
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

    if 'Next Image' in but:
        #skip_im = 0     # this flag stops detecting the current image to move on to the next one
        cv2.destroyAllWindows()
        global pic
        pic = getImage()
        
    elif 'Save Parameters' in but:
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
        #root_2.destroy()
        root_2.quit()
        root.destroy()
        #lambda: root_2.destroy()
        cv2.destroyAllWindows()
    
    updateStatusDisplay()
    mainDetection() #detect script
    return

######################### creating the button display ########################
def doMouse(event,x,y,flags,param):
    global xc,yc
    
    if event == cv2.EVENT_LBUTTONDOWN:
        #xc,yc = x*FULL_SCALE,y*FULL_SCALE # compensate for full scale scaling
        mainDetection()
    return 

'''
def button_display(): #compiled the mainloop into a function
    global root_2
    root_2 = tk.Tk() #root is for file manager, root_2 is for button grid
    v = tk.IntVar()
    v.set(2)            # set choice to "+1 Frame"
    
    root_2.title("Detection Functions")
    updateStatusDisplay()
    
    for val, txt in enumerate(names): #goes through each button (and what they'd look like)
        r=int(1+val/4)
        c=int(val%4)
        tk.Radiobutton(root_2, text=txt,padx = 1, variable=v,width=BUTTON_WIDTH,command=doButton,indicatoron=0,value=val).grid(row=r,column=c)
    
    cv2.setMouseCallback('Full Image',doMouse)
    return
'''
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
    print('Click "Save Parameters" to save the objects detected into the csv file')
    print('Click "Next Image" to go to the next image')
    print('Hit the X in the top right corner to end program')
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
    ("Save Parameters"),
    ("Next Image"),
    ("Exit"), 
    (" "), 
    (" "),
    (" "),
    (" ")
]

################################## MAIN #####################################

doc() #to print the user guide

pic = getImage()

root_2 = tk.Toplevel() #root is for file manager, root_2 is for button grid
v = tk.IntVar()
#v.set(2)            # set choice to "+1 Frame"

root_2.title("Detection Functions")
updateStatusDisplay()

for val, txt in enumerate(names): #goes through each button (and what they'd look like)
    #print('Names:',names)
    #print('Val:',val)
    #print('Text:',txt)
    r=int(1+val/4)
    c=int(val%4)
    tk.Radiobutton(root_2, text=txt,padx = 1, variable=v,width=BUTTON_WIDTH,command=doButton,indicatoron=0,value=val).grid(row=r,column=c)

mainDetection()
cv2.setMouseCallback('Full Image',doMouse)
print('End of loop')

root_2.mainloop() #program will keep waiting until a button has been pressed
#print('Out of loop')
cv2.destroyAllWindows()     # clean up to end program

print('Done with images.') #once the program ends
#np.savetxt(detectFileName,detectArray,header=detectHeader,delimiter=',')

#saves data into the csv file
print('Saving data to CSV file ...')
detectDF = pd.DataFrame(detectList, columns = detectHeader)
detectDF.to_csv(detectFileName, columns = detectHeader,header = True)

print('bye!')               # tell the user program has ended

