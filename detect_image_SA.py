# -*- coding: utf-8 -*-
"""
Detect script but for images
Created on Tue Oct 12 12:18:53 2021

@author: salma

v1.0
This script should detect objects for an image. In the future, it might be a module
added to the final detect script?
"""
import cv2
import numpy as np
import keyboard_SA as k 
import tkinter as tk
from tkinter import filedialog

################################## GET IMAGE #######################
def getImage():
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename() #the file you choose is in the form of the pathway string
    print('File chosen:',file)
    try:
        image = cv2.imread(file)
        return image
    except AttributeError:
        return 'Must be a jpg or a png!'
#pic = 'black_mountain.jpg'    

#################### CSV FILE NAME AND IMAGE RES ##############################
detectFileName='detection_image.csv'      # output file containing object location, area, aspect ratio for each piceo frame
X_REZ=640; Y_REZ=480;               # viewing resolution
THICK=1                             # bounding box line thickness
BLUR=7                              # object bluring to help detection
VGA=(640,480)
PROCESS_REZ=(320,240)
    
############################ DEFINE VARIABLES ################################
detectHeader= 'IMAGE #,ID,X0,Y0,X1,Y1,XC,YC,AREA,AR,ANGLE'
FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; AREA=8; AR=9; ANGLE=10; MAX_COL=11 # pointers to detection features
detectArray=np.empty((0,MAX_COL), dtype='int')  # detection features populated with object for each frame

################################## MAIN #####################################
print('''
How to use keyboard to adjust threshold.....
Click on image to enable keyboard.
Press 't' to select threshold.
Press 'a' to set t:he minimmum area of an object
Press 'A' to set the maximum area of an object
Press 'n' to move on to the next image
Press '+' and '-' to change value by increments of 1.
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

################## start capturing frames of video #############################
frameCount=0                        # keeps track of frame number
#while True:    # process each frame until end of video or 'q' key is pressed
for i in range(3):
    pic = getImage()
    #pic = cv2.imread('black_mountain.jpg')
    if pic is None:
        break
    else:
        while k.run:
            # check for key activity that changes program variables
            (thresh,MIN_AREA,MAX_AREA,y)=k.processKey()   # a and A are used to change the min and max sizes for the detection 
            
            # blur and threshold image
            colorIM=cv2.resize(pic,PROCESS_REZ)
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
                    
                    # create an if statement here to save threshold
                    
                    # save object parameters in detectArray in format FRAME=0; ID=1;  X0=2;   Y0=3;   X1=4;   Y1=5;   XC=6;   YC=7; CLASS=8; AREA=9; AR=10; ANGLE=11; MAX_COL=12
                    parm=np.array([[i,objCount,x0,y0,x1,y1,xc,yc,area,ar,angle]],dtype='int') # create parameter vector (1 x MAX_COL) 
                    detectArray=np.append(detectArray,parm,axis=0)  # add parameter vector to bottom of detectArray, axis=0 means add row
                    objCount+=1                                     # indicate processed an object
            #print('frame:',frameCount,'objects:',len(contourList),'big objects:',objCount)
        
            # shows results
            cv2.imshow('colorIM', cv2.resize(colorIM,VGA))      # display image
            #cv2.imshow('blurIM', cv2.resize(blurIM,VGA)) # display thresh image
            cv2.imshow('binaryIM', cv2.resize(binaryIM,VGA))# display thresh image
            
            frameCount+=1
            #cv2.waitKey(0)
            
    k.run = not k.run
    cv2.destroyAllWindows()
# program ending, test why
if frameCount>0:            # normal ending, save detection file
    print('Done with video. Saving feature file and exiting program')
    np.savetxt(detectFileName,detectArray,header=detectHeader,delimiter=',', fmt='%d')
else:                       # abnormal ending, don't save detection file
    print('No image found...')

cv2.destroyAllWindows()     # clean up to end program
print('bye!')               # tell the user program has ended









