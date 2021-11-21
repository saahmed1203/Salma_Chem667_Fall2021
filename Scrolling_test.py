# -*- coding: utf-8 -*-
"""

Script to test out Tkinter scrolling

Created on Sun Nov 21 10:07:32 2021

@author: salma
"""

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry('300x300')
root.title('Slider Test')

v = tk.DoubleVar() #to get values (used in detect script)
sec_var = tk.DoubleVar()

def print_val(event):
    label.configure(text='Current value: '+ str(int(v.get())))
    label_2.configure(text='Current value: '+ str(int(sec_var.get())))

# Slider 1
slider = ttk.Scale(root, from_=0, to=100, orient='horizontal', 
                   length = 200,variable=v,command=print_val)

label = tk.Label(root,text='Current value: ' + str(int(v.get())))

# Slider 2
slider_2 = ttk.Scale(root, from_=0, to=100, orient='vertical', 
                    length = 200,variable=sec_var,command=print_val)

label_2 = tk.Label(root,text='Current value: ' + str(int(sec_var.get())))

slider.pack()
label.pack()
slider_2.pack()
label_2.pack()
root.mainloop()



