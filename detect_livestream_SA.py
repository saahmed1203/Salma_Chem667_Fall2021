# -*- coding: utf-8 -*-
"""
Detect script using livestream
Created on Mon Oct 18 12:07:21 2021

@author: salma

v1.0
This script takes the livestream input of the microscope and returns the detect csv
file. The user can press 's' to start/pause saving objects in the livestream, and then
press 'q' to quit the program.

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

#################### start detecting objects (livestream) #############################

#adding cv2.CAP_DSHOW makes windows open faster and output does not have any errors,
#but in exchange, the camera quality is lowered, including the fps

cap = cv2.VideoCapture(1)           # start video file reader (currently livestream)
#cap = cv2.VideoCapture('fiveSecondPlankton.mp4')
cap.set(3, 1920); cap.set(4, 1080); # set to 1080p resolution
frameCount=0                        # keeps track of frame number
while(cap.isOpened() and k.run):    # process each frame until end of video or 'q' key is pressed
    # check for key activity that changes program variables
    (thresh,MIN_AREA,MAX_AREA,y)=k.processKey()   # a and A are used to change the min and max sizes for the detection
    
    # get image
    ret, colorIM = cap.read()
    if not ret:                     # check to make sure there was a frame to read
        print('Can not find video or we are all done')
        break
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
            if k.save:
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
    
    if k.save: #so that the frames in the output csv file are in order
        frameCount+=1
    #cv2.waitKey(500) #slows down object detection
    
# program ending, test why
if frameCount>0:            # normal ending, save detection file
    print('Done with livestream. Saving feature file and exiting program')
    np.savetxt(temp_name,detectArray,header=detectHeader,delimiter=',', fmt = '%d') #original csv
    #detectDF = pd.DataFrame(detectList, columns = detectHeader)
    #detectDF.to_csv(detectFileName, columns = detectHeader,header = True)
else:                       # abnormal ending, don't save detection file
    print('No video input found...')

cv2.destroyAllWindows()             # clean up to end program
cap.release()
print('video closed')               # tell the user program has ended

############################## ID TRACKER ####################################
if frameCount > 0:
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
    print('max frames',maxFrames)
    #for i in range(10): #to test loop
    for i in range(maxFrames-1): #to prevent frames from being repeated
        obj_data = np.where(data[:,FRAME] == i) #current frame index
        obj_next_data = np.where(data[:,FRAME] == i + 1) #next frame index
        #print(obj_data)
        for item in range(len(obj_data)):
            #print(obj_data)
            #print(item)
            first_ref = data[obj_data[item],ID]
            second_ref = data[obj_next_data[item],ID]
        #print('Ref 1:',obj_data,first_ref)
        #print('Ref 2:',obj_next_data, second_ref)
            X_frame1 = all_x_data[obj_data[item]] #all X's in frame i
            Y_frame1 = all_y_data[obj_data[item]] #all Y's in frame i
            X_frame2 = all_x_data[obj_next_data[item]] #all X's in frame i + 1
            Y_frame2 = all_y_data[obj_next_data[item]] #all Y's in frame i + 1
            #print('X_frame1:', X_frame1)
            #print('Y_frame1:',Y_frame1)
            #print('X_frame2:',X_frame2)
            #print('Y_frame2:',Y_frame2)
            for j in range(len(X_frame1)): #for each x value in frame i
                if not (i == 0 and j == 0): #so the counter starts at 0 for the 0th frame, 0th object
                    ind_counter += 1
                X1 = X_frame1[j]
                Y1 = Y_frame1[j]
                dist_dict = {}
                for p in range(len(X_frame2)): #for each x value in frame i + 1
                    X2 = X_frame2[p]
                    Y2 = Y_frame2[p]
                    #print('X1:',X1)
                    #print('X2:',X2)
                    #print('Y1:',Y1)
                    #print('Y2:',Y2)
                    distance = dist(X1,Y1,X2,Y2)
                    dist_dict[p] = distance #assigns each object with a distance
                    
                #here I need to sort out the dictionary by values (i.e. by distance)
                dist_list = sorted(dist_dict.items(), key = lambda x:x[1])
                
                #here shows the object in frame i compared to all the objects in frame i + 1
                #print('Frame',i,'Obj:',j,'(next obj, dist):',dist_list) #this is of the sorted list
                #print('ind_counter', ind_counter)
                
                #here is the where I updated the ID number
                data[ind_counter,ID] = dist_list[0][0] #the object associated with the shortest distance
    
    #creating the new 'HW6_track_SA.csv' file
    np.savetxt(detectFileName, data, fmt= '%d', header = detectHeader, delimiter = ',')
    print(' ')
    print('File with updated IDs was created successfully!')


print('bye!')







