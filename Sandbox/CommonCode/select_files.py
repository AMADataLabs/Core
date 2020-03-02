# Kari Palmier    Created 8/22/19
#
#############################################################################
import tkinter as tk
from tkinter import filedialog

def select_files(init_file_dir, message_text):
        
    message_prompt =  message_text + '? (y/n): '

    root = tk.Tk()
    root.withdraw()

    sel_flag = False
    out_list = []
    while sel_flag == False:
        
        file_str = ''
        while file_str.find('y') < 0 and file_str.find('n') < 0:
            file_str = input(message_prompt)
            file_str = file_str.lower()
            
        
        if file_str.find('y') >= 0:
            temp_list = filedialog.askopenfilenames(initialdir = init_file_dir,
                                         title = "Choose file(s)...")
            
            if temp_list != '':
                temp_list = list(temp_list)
                
                for temp_file in temp_list:                
                    out_list.append(temp_file)
        
        else:
            sel_flag = True
                             
    return out_list
