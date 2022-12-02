# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 16:18:46 2022

@author: salma
"""

import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

#to select csv file
#root = tk.Tk()
#root.withdraw()

#csv_file = filedialog.askopenfilename() #the main function
#print('CSV filename:', csv_file)

#root.destroy()

csv_file = 'C:/Users/salma/OneDrive/Desktop/stentor_test.csv'

#to plot the objects
tracker_df = pd.read_csv(csv_file)
print(tracker_df.head())

#find all the unique ID numbers
unique_ids = tracker_df['ID'].unique()
unique_ids = list(unique_ids)
print(unique_ids)

#filter the dataframe with respect to each ID number
for ID in unique_ids:
    ID = int(ID)
    print('ID:',ID, 'data type:',type(ID))
    filt_df = tracker_df[tracker_df['ID'] == ID]
    #plot each filtered dataset
    plt.scatter(filt_df['XC'],filt_df['YC'], label = ID)

#customize the graph "box
plt.legend()
plt.xlabel('x-coord for object')
plt.ylabel('y-coord for object')
plt.show()

