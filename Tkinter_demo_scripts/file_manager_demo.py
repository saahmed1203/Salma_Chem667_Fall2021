# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 15:11:48 2022

@author: salma
"""
import tkinter as tk
from tkinter import filedialog

############################## CREATING WINDOWS ###################################
root = tk.Tk()              # this creates a widget
root.withdraw()             # this hides the widget once it's created (but it's still active!)

#note: file manager only works on Windows and Linux
file = filedialog.askopenfilename()     # creates the file manager window (using the root widget)
print()
print('File pathway:', file)

root.destroy()

print('Exiting program...')
print('Bye!')
