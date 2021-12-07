# -*- coding: utf-8 -*-
"""
Tkinter module demo (file manager root, and having multiple roots)

Link for other functions besides buttons:
https://www.pythontutorial.net/tkinter/tkinter-ttk/ 

Created on Wed Nov  3 13:14:43 2021

@author: salma
"""

import tkinter as tk
from tkinter import filedialog
import cv2

########################## DEFINING BUTTON FUNCTIONS ###########################
x = 0
def addFunction():        # defining button functions (the Add +1 button)
    global x, main_label
    x += 1
    main_label['text'] = 'X Value = ' + str(x) # to update the window label
    return 

def close_3rd_window():   # defining the button to close the third window 
    third_root.withdraw()
    third_root.quit()
    return

def open_3rd_window():    # defining the button to open a third window (from the second window)
    global third_root
    
    #to create a third window (on top of the second one)
    third_root = tk.Toplevel(second_root)   # to specify that this window goes on top of the second window!
    third_root.title('Third Window')
    third_root.geometry('300x200')
    
    #creating the labels and buttons for the third window
    new_label = tk.Label(third_root, text = 'A new window has been opened!')
    close_button = tk.Button(third_root, text = 'Close', command = close_3rd_window)
    new_label.pack()
    close_button.pack()
    
    third_root.mainloop() #to loop in the button panel until the user exits
    return

def quitProgram():          # defining the exit button (for the second window)
    second_root.withdraw()
    second_root.quit()
    root.destroy()
    return

############################## CREATING WINDOWS ###################################

# Creating a single root (file manager example)
root = tk.Tk()              # this creates a widget
root.withdraw()             # this hides the widget once it's created (but it's still active!)
#file = filedialog.askopenfilename()     # creates the file manager window (using the root widget)
#print()
#print('File pathway:', file)

#to view file
#cv2.imshow('Image chosen:',cv2.imread(file))
#cv2.waitKey(0)

#'''
#creating a second window
second_root = tk.Toplevel()     # this creates a second widget on top of the "root"
second_root.title('Second Window')  # window title
second_root.geometry('300x200')     # window size

#adding the buttons and labels to the toplevel window
main_label = tk.Label(second_root, text = 'X Value = ' + str(x)) #the x value updates in the window
button = tk.Button(second_root, text = 'Add +1', command = addFunction) #the "Add +1" button

#button to create a new window!
new_wind_button = tk.Button(second_root, text = 'Open new window', command = open_3rd_window) #the "Add +1" button
exit_button = tk.Button(second_root,text = 'Exit', fg = 'coral',command = quitProgram) #the "Exit" button

#to put all of the buttons and labels in the window
main_label.pack()
button.pack()
new_wind_button.pack()
exit_button.pack()

second_root.mainloop() #to loop in the button panel until the user exits
#'''

print('Exiting program...')
print('Bye!')

