# -*- coding: utf-8 -*-
"""
File Manager Dropdown Script
Created on Sun Oct 10 12:07:31 2021
@author: salma

v1.0
Opens a file manager window where the user can view all files in the current directory
and allows the user to choose a file (images only so far) from the current or a DIFFERENT 
directory and view it using OpenCV. So far, this works for PC, need to test it on a Mac.

"""

import cv2
import os
import tkinter as tk
from tkinter import filedialog

#creating the file manager popup window (using tkinter)
root = tk.Tk()
root.withdraw()
print('Working directory:',os.getcwd())
file = filedialog.askopenfilename() #the file you choose is in the form of the pathway string
print('File chosen:',file)

#viewing the selected image
try:
    image = cv2.imread(file)
    #print('Image size',image.shape)
    raw_dim = image.shape
    new_dim = (int(raw_dim[0]/4),int(raw_dim[1]/4))
    #print('New image size:',new_dim)
    cv2.imshow('Selected image (resized to fit window)',cv2.resize(image,new_dim))
    #cv2.imshow('Selected image (original)',image)
    cv2.waitKey(0)
    print('Program closed. Bye!')
except AttributeError:
    print(' ')
    print('Error, file must be an image (i.e. jpeg or a png)')
    
    
    
    

