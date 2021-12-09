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
but_val = tk.IntVar()

button_names = [('Say Hi!'),('Say Bye!')]

def print_val(event):
    label.configure(text='Current value: '+ str(int(v.get())))
    label_2.configure(text='Current value: '+ str(int(sec_var.get())))

def button_stuff():
    b_val = but_val.get()
    button = button_names[b_val]
    if 'Hi' in button:
        label_3['text'] = 'Hi there!'
    elif 'Bye' in button:
        label_3['text'] = 'Bye for now!'
    return

# Slider 1
slider = ttk.Scale(root, from_=0, to=100, orient='horizontal', 
                   length = 200,variable=v,command=print_val)
slider.grid(row=0)

label = tk.Label(root,text='Current value: ' + str(int(v.get())))
label.grid(row=1)

# Slider 2
slider_2 = ttk.Scale(root, from_=0, to=100, orient='horizontal', 
                    length = 200,variable=sec_var,command=print_val)
slider_2.grid(row=2)

label_2 = tk.Label(root,text='Current value: ' + str(int(sec_var.get())))
label_2.grid(row=3)

#getting buttons too
for val, txt in enumerate(button_names): #goes through each button (and what they'd look like)
    r=int(4+val/2)
    c=int(val%2)
    tk.Radiobutton(root, text=txt,padx = 1, variable=but_val,
                   command=button_stuff,indicatoron=False,value=val).grid(row=r,column=c)
    
label_3 = tk.Label(root,text = '')
label_3.grid(row=5)

root.mainloop()



