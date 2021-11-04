# -*- coding: utf-8 -*-
"""
Tkinter module demo (file manager root, and having multiple roots)

Created on Wed Nov  3 13:14:43 2021

@author: salma
"""

import tkinter as tk
from tkinter import filedialog

x = 0
def addFunction():          # defining button functions (the Add +1 button)
    global x, main_label
    x += 1
    main_label['text'] = 'X Value = ' + str(x) # to update the window label
    return 

def quitProgram():          # defining the exit button
    second_root.withdraw()
    second_root.quit()
    root.destroy()
    return


# Creating a single root (file manager example)
root = tk.Tk()              # this creates a widget
root.withdraw()             # this hides the widget once it's created (but it's still active!)
file = filedialog.askopenfile()     # creates the file manager window (using the root widget)
print()
print('File pathway:', file)

#'''
#creating a second window
second_root = tk.Toplevel()     # this creates a second widget on top of the "root"
second_root.title('Second Window')  # window title
second_root.geometry('300x200')     # window size

#adding the buttons and labels to the toplevel window
main_label = tk.Label(second_root, text = 'X Value = ' + str(x)) #the x value updates in the window
button = tk.Button(second_root, text = 'Add +1', command = addFunction) #the "Add +1" button
exit_button = tk.Button(second_root,text = 'Exit', fg = 'coral',command = quitProgram) #the "Exit" button

#to put all of the buttons and labels in the window
main_label.pack()
button.pack()
exit_button.pack()

second_root.mainloop() #to loop in the button panel until the user exits
#'''

print('Exiting program...')
print('Bye!')

