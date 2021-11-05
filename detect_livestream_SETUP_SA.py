# -*- coding: utf-8 -*-
"""
Detect script SET UP
Created on Thurs Nov 4 2:07:21 2021

@author: salma

"""
import cv2
import numpy as np
#import pandas as pd
import keyboard_SA as k

#################### CSV FILE NAME AND IMAGE RES ##############################
detectFileName='detection_livestream_updatedID.csv'      # output file containing object location, area, aspect ratio for each piceo frame
temp_name = 'raw_livestream_detection.csv'
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

################################## MAIN #####################################
print('''
How to use keyboard to adjust threshold.....
Click on image to enable keyboard.
Press 't' to select threshold.
Press 'a' to set the minimmum area of an object
Press 'A' to set the maximum area of an object
Press '+' and '-' to change value by increments of 1.
Press 's' to start saving the objects detected (but not the video!)
Hold shift while pressing '+' or '-' to change value by increments of 10. 
Press 'q' to quit
''')

def getAR(obj):
    ((xc,yc),(w,h),(angle)) = cv2.minAreaRect(obj)  # get parameters from min area rectangle
    ar=0.0      # initialize aspect ratio as a floating point so calculations are done in floating point
    # calculate aspect ratio (always 1 or greater)
    if w>=h and h>0:
        ar=w/h
    elif w>0:
        ar=h/w
    return(xc,yc,ar,angle)         

def dist(point1, point2, point3, point4): #to find distance between objects
    x1 = float(point1)
    y1 = float(point2)
    x2 = float(point3)
    y2 = float(point4)
    arg = (x2 - x1)**2 + (y2 - y1)**2
    dist = arg**0.5
    return dist
    #print('Distance between points:',dist)

########################## SET UP FOR MOUSE SCRIPT #############################

#adding cv2.CAP_DSHOW makes windows open faster and output does not have any errors,
#but in exchange, the camera quality is lowered, including the fps

def opening_video():
    global cap
    #cap = cv2.VideoCapture(1)           # start video file reader (currently livestream)
    cap = cv2.VideoCapture('fiveSecondPlankton.mp4')
    cap.set(3, 1920); cap.set(4, 1080); # set to 1080p resolution
    return
    
def frame_processing(): 
    global detectArray
    frameCount=0                        # keeps track of frame number
    #while(cap.isOpened() and k.run):    # process each frame until end of video or 'q' key is pressed
    
    # check for key activity that changes program variables
    (thresh,MIN_AREA,MAX_AREA,y)=k.processKey()   # a and A are used to change the min and max sizes for the detection
    
    # get image
    ret, colorIM = cap.read()
    if not ret:                     # check to make sure there was a frame to read
        print('Can not find video or we are all done')
        #break
    #print('original size:',colorIM.shape)
    # blur and threshold image
    colorIM=cv2.resize(colorIM,PROCESS_REZ)
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
            if k.save: # change to save when creating buttons
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

    frameCount+=1
    cv2.waitKey(0) #waits for user to close windows
    return

#testing the functions
opening_video()
frame_processing()

cv2.destroyAllWindows()             # clean up to end program
cap.release()
print('video closed')               # tell the user program has ended

