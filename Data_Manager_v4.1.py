#Data Manager created by Allesandro Yudo | IFRS17 Team

import os
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Label
from tkinter import ttk
import zipfile
import pandas as pd
import win32com.client as win32
from tqdm import tqdm
import time
import csv
import re

class CopyMoveDialog(tk.simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="Do you want to copy or move all files?").pack()

        self.action_var = tk.StringVar()
        copy_button = ttk.Radiobutton(master, text="Copy", variable=self.action_var, value="copy")
        copy_button.pack()

        move_button = ttk.Radiobutton(master, text="Move", variable=self.action_var, value="move")
        move_button.pack()

        return copy_button  # initial focus

    def apply(self):
        selected_action = self.action_var.get()
        if selected_action == "copy":
            self.copy = True
            self.move = False
        elif selected_action == "move":
            self.copy = False
            self.move = True
        else:
            self.copy = False
            self.move = False

class FACSplitDialog(tk.simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="Choose option to split if data more than 1M rows").pack()

        self.action_var = tk.StringVar()
        file_button = ttk.Radiobutton(master, text="Split by File", variable=self.action_var, value="file")
        file_button.pack()

        sheet_button = ttk.Radiobutton(master, text="Split by Sheet", variable=self.action_var, value="sheet")
        sheet_button.pack()

        return file_button  # initial focus

    def apply(self):
        selected_action = self.action_var.get()
        if selected_action == "file":
            self.file = True
            self.sheet = False
        elif selected_action == "sheet":
            self.file = False
            self.sheet = True
        else:
            self.file = False
            self.sheet = False            

class ExtDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, directory):
        self.directory = directory
        self.selected_extensions = ()
        super().__init__(parent)

    def list_files(self, directory):
        files_list = []
        for root, _, files in os.walk(directory):
            for filename in files:
                files_list.append(os.path.join(root, filename))
        return files_list

    def select_files(self):
        selected_files = []
        for extension, var in self.extension_vars.items():
            if var.get():
                selected_files.append(extension)
        self.selected_extensions = tuple(selected_files)  # Update selected_extensions

        print("Selected files:", self.selected_extensions)

    def body(self, master):
        self.files = self.list_files(self.directory)
        unique_extensions = set(os.path.splitext(filename)[1] for filename in self.files)

        tk.Label(master, text="Select Format:").grid(row=0, column=0, sticky="w")  # Use grid for label

        self.extension_vars = {}
        for i, file_extension in enumerate(unique_extensions):
            var = tk.BooleanVar()
            self.extension_vars[file_extension] = var
            cb = tk.Checkbutton(master, text=file_extension, variable=var)
            cb.grid(row=i+1, column=0, sticky="w")  # Use grid for checkbuttons

        return 

class FSDialog(tk.simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="File Type:").pack()

        self.action_var = tk.StringVar()
        fs06_button = ttk.Radiobutton(master, text="FS06", variable=self.action_var, value="fs06")
        fs06_button.pack()

        fs165_button = ttk.Radiobutton(master, text="FS16.5", variable=self.action_var, value="fs165")
        fs165_button.pack()

        return fs06_button  # initial focus

    def apply(self):
        selected_action = self.action_var.get()
        if selected_action == "fs06":
            self.fs06 = True
            self.fs165 = False
        elif selected_action == "fs165":
            self.fs06 = False
            self.fs165 = True
        else:
            self.fs06 = False
            self.fs165 = False            


class DataManager:
    def __init__(self, master):
    # General App Styling
        self.master = master
        master.title("Data Manager")
        master.geometry('500x420')
        master.configure(bg="#F0F0F0")  # Setting a light gray background color

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=10)
        style.configure("TLabel", font=("Arial", 10), background="#F0F0F0")

        self.label = ttk.Label(master, text="Welcome To Data Manager", font="Arial 20 bold", foreground="dark orange")
        self.label.grid(row=0, column=0, columnspan=6, pady=10, padx=10)
        self.label2 = ttk.Label(master, text="Copyright By: IFRS17 Team", font="Arial 10 bold", foreground="dark orange")
        self.label2.grid(row=1, column=0, columnspan=6, pady=10, padx=10)

        info_labels = [
            ""
        ]

        for index, text in enumerate(info_labels, start=1):
            ttk.Label(master, text=text).grid(row=index, column=0, columnspan=6, sticky='w', pady=5, padx=20)

        # Directory Button and Label
        self.choose_directory_button = ttk.Button(master, text="Choose Your Folder", command=self.set_directory)
        self.choose_directory_button.grid(row=20, column=0, pady=5, padx=5,sticky="w")
        self.directory_label = ttk.Label(master, text="")
        self.directory_label.grid(row=25, column=0, padx=20, sticky="w")
        # Merge Button
        self.relocate_button = ttk.Button(master, text="Files Relocate", command=self.files_relocate)
        self.relocate_button.grid(row=45, column=0, pady=20, padx=20, sticky="w")
        
        self.filesrename_button = ttk.Button(master, text="Files Rename", command=self.files_rename)
        self.filesrename_button.grid(row=45, column=1, pady=20, padx=20, sticky="w")
        
        self.fileszip_button = ttk.Button(master, text="Files Zip", command=self.files_zip)
        self.fileszip_button.grid(row=45, column=2, pady=20, padx=20, sticky="w")         

        self.break_conven_button = ttk.Button(master, text="Break Conven", command=self.break_conven)
        self.break_conven_button.grid(row=50, column=0, pady=20, padx=20, sticky="w")

        self.hdr_updater_button = ttk.Button(master, text="HDR Update", command=self.hdr_updater)
        self.hdr_updater_button.grid(row=50, column=1, pady=20, padx=20, sticky="w")

        self.hdr_compiler_button = ttk.Button(master, text="HDR Compile", command=self.hdr_compiler)
        self.hdr_compiler_button.grid(row=50, column=2, pady=20, padx=20, sticky="w")        

        self.date_fixer_button = ttk.Button(master, text="Date Fixer", command=self.date_check)
        self.date_fixer_button.grid(row=55, column=0, pady=20, padx=20, sticky="w") 

        self.fac_reader_button = ttk.Button(master, text="FAC to XLSB", command=self.fac_reader)
        self.fac_reader_button.grid(row=55, column=1, pady=20, padx=20, sticky="w") 

        self.csv_split_button = ttk.Button(master, text="CSV Split", command=self.csv_split)
        self.csv_split_button.grid(row=55, column=2, pady=20, padx=20, sticky="w")

        self.directory = None
#         master.grid_columnconfigure(3, weight=1)
#         master.grid_rowconfigure(3, weight=1)

    def set_directory(self):
        self.directory = filedialog.askdirectory(title="Choose Your Folder")
        num_files = len([f for f in os.listdir(self.directory)])
        self.directory_label.config(text=f"Number of files/folder: {num_files}")    

    def files_relocate(self):
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the Folder first.")
            return
        
        relocate_option = messagebox.askyesno("Files Relocate", "This will relocate all files inside folders in chosen folder to a new folder. Continue ?")
        
        if relocate_option:    
#             inner_files = None
            new_list = []
            new_folder_name = ""
            new_folder_name2 = ""
            base_path = self.directory

            # List all the directories in the base path
            sub_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

            dialog = CopyMoveDialog(self.master)
            
            if dialog.copy and dialog.move:
                messagebox.showwarning("Warning", "Please choose either Copy or Move.")
                return
            # If either copy or move option is selected, proceed with ExtDialog
            ext_dialog = ExtDialog(root, self.directory)
            ext_dialog.select_files()

            # Access the selected_extensions attribute from ExtDialog
            selected_extensions = ext_dialog.selected_extensions
            print(selected_extensions)
            # Loop through each sub folder
            for folder in sub_folders:
                # Full path to the current year-month folder
                full_folder_path = os.path.join(base_path, folder)

                files_in_folder = [f for f in os.listdir(full_folder_path) if os.path.isfile(os.path.join(full_folder_path, f)) and f.endswith(selected_extensions)]

                if files_in_folder:
                    # print(file)
                    if dialog.move:
                        
                        # If no subfolders, create a new folder named "All Files"
                        new_folder_name2 = "All Files"
                        new_folder_path = os.path.join(base_path, new_folder_name2)
                        if not os.path.exists(new_folder_path):
                            os.makedirs(new_folder_path)
                            print(f"Created folder: {new_folder_path}")
                        else:
                            print(f"Folder already exists: {new_folder_path}")
                            # Move all files in the current folder to the "All Files" folder
                        for file_in_folder in os.listdir(full_folder_path):
                            if file_in_folder.endswith(selected_extensions):
                                path_inner_files = os.path.join(full_folder_path, file_in_folder)
                                # print(f"inner path: {path_inner_files}")
                                if os.path.isfile(path_inner_files):
                                    shutil.move(path_inner_files, os.path.join(new_folder_path, file_in_folder))
                                    print(f"Moved file {file_in_folder} to {new_folder_path}") 

                    elif dialog.copy:

                        # If no subfolders, create a new folder named "All Files"
                        new_folder_name2 = "All Files - copy"
                        new_folder_path = os.path.join(base_path, new_folder_name2)
                        if not os.path.exists(new_folder_path):
                            os.makedirs(new_folder_path)
                            print(f"Created folder: {new_folder_path}")
                        else:
                            print(f"Folder already exists: {new_folder_path}")
                        # Move all files in the current folder to the "All Files" folder
                        for file_in_folder in os.listdir(full_folder_path):
                            if file_in_folder.endswith(selected_extensions):
                                path_inner_files = os.path.join(full_folder_path, file_in_folder)
                                # print(f"inner path: {path_inner_files}")
                                if os.path.isfile(path_inner_files):
                                    shutil.copy2(path_inner_files, os.path.join(new_folder_path, file_in_folder))
                                    print(f"Copied file {file_in_folder} to {new_folder_path}") 

                inner_folders = [f for f in os.listdir(full_folder_path) if os.path.isdir(os.path.join(full_folder_path, f))]
#                 print(inner_folders)
                # Loop through each inner folder within the current year-month folder
                for inner_folder in inner_folders:
                    full_inner_path = os.path.join(full_folder_path, inner_folder)

#                     print(full_inner_path)

                    
                    if dialog.move:
                                             
                        for filename in os.listdir(full_inner_path):
                            if filename.endswith(selected_extensions):
                                new_folder_name = f"{inner_folder} all copy"                               
                                new_folder_path = os.path.join(base_path, new_folder_name)                                 
                                if not os.path.exists(new_folder_path):
                                    os.makedirs(new_folder_path)
                                    new_list.append(new_folder_name)
                                    print(f"Created folder: {new_folder_path}")                               
                                shutil.move(os.path.join(full_inner_path, filename), new_folder_path)

           
                                
                    elif dialog.copy:                     
                        
                        for filename in os.listdir(full_inner_path):
                            if filename.endswith(selected_extensions):
                                new_folder_name = f"{inner_folder} all copy"                               
                                new_folder_path = os.path.join(base_path, new_folder_name)                                 
                                if not os.path.exists(new_folder_path):
                                    os.makedirs(new_folder_path)
                                    new_list.append(new_folder_name)
                                    print(f"Created folder: {new_folder_path}")                              
                                
                                shutil.copy2(os.path.join(full_inner_path, filename), new_folder_path)

                              
                    
            print("Done!")
            messagebox.showinfo("Info", f"Done Processing. Created new folder: {new_list}, {new_folder_name2}")
        else:
            return

    def files_rename(self):
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the Folder first.")
            return

        rename_option = messagebox.askyesno("Files Rename", "This will replace all csv / hdr files' names with specific text in the chosen folder. Continue?")
        file_extensions = ['.csv', '.hdr']
        if rename_option:
            base_path = self.directory

            base_text = simpledialog.askstring("Text to Replace", "Enter the text you want to replace:")
            replace_text = simpledialog.askstring("Replacement Text", "Enter the text to replace it with:")

            for filename in os.listdir(base_path):
                file_extension = os.path.splitext(filename)[1]
                if file_extension in file_extensions:  # You need to define file_extensions
                    new_filename = filename.replace(base_text, replace_text)
                    old_filepath = os.path.join(base_path, filename)
                    new_filepath = os.path.join(base_path, new_filename)
                    os.rename(old_filepath, new_filepath)
                    print(f'Renamed file: {filename} -> {new_filename}')
            print("Done!")
            messagebox.showinfo("Info", f"Done Processing. Replaced: {base_text} to {replace_text}")                    
        else:
            return

        
        
    def files_zip(self):
        
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the Folder first.")
            return
        
        zip_option = messagebox.askyesno("Files Zip", "This will zip all csv / hdr files in the chosen folder to their respective files name, continue ?")
        
        if zip_option:  
            
            base_path = self.directory      
            
            for filename in os.listdir(base_path):
                if filename.endswith('.csv'):
                    base_name = os.path.splitext(filename)[0]  # Get the base name without extension
                    zip_name = os.path.join(base_path, f'{base_name}.zip')  # Create the zip file name
                    with zipfile.ZipFile(zip_name, 'w') as zipf:
                        csv_file = os.path.join(base_path, filename)
                        hdr_file = os.path.join(base_path, f'{base_name}.hdr')
                        zipf.write(csv_file, arcname=os.path.basename(csv_file))
                        zipf.write(hdr_file, arcname=os.path.basename(hdr_file))
                        print(f'Zipped file: {filename}')
            print("Done!")
            messagebox.showinfo("Info", f"Done Processing. All .csv or .hdr files zipped")               
        else:
            return
        
    def break_conven(self):
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the Folder first.")
            return

        rename_option = messagebox.askyesno("Break Conven", "This will separate Syariah and Non Syariah Data in two new folders. Continue?")
         # Iterate through all files in the FS06 directory
        if rename_option:
            source_folder = self.directory
            dialog = FSDialog(self.master)
            if dialog.fs06:
                syariah_folder = os.path.join(source_folder, "Syariah")
                non_syariah_folder = os.path.join(source_folder, "Non Syariah")

                # Create the 'Syariah' and 'Non Syariah' folders if they do not exist
                os.makedirs(syariah_folder, exist_ok=True)
                os.makedirs(non_syariah_folder, exist_ok=True)

                # List of values to filter on
                syariah_values = [
                    "ZRB1", "ZRT1", "ZST1", "ZRD1", "ZSD1",
                    "ZHSB", "ZHCB", "ZC01", "ZC02", "ZC03", "ZC04",
                    "ZRB3", "ZRT3", "ZST3", "ZRB2", "ZRT2", "ZST2",
                    "ZAD1", "ZRB4", "ZRT4", "ZST4", "ZCI1", "ZCI2",
                    "ZWO1", "ZWO2", "ZWOP", "ZWPP", "ZPT1", "ZFT1",
                    "ZWP1", "ZWP2", "ZHSC", "ZHSA", "ZE01", "ZE02",
                    "ZWO4", "ZWO5", "ZEP2", "ZEP3", "BTN3"
                ]

                # Process each file
                for filename in os.listdir(source_folder):
                    if filename.endswith('.csv'):
                        print(f"Processing Data {filename}")
                        file_path = os.path.join(source_folder, filename)
                        df = pd.read_csv(file_path, encoding= 'utf-8-sig', dtype=str, keep_default_na=False, na_values=[''], low_memory=False)

                        # Filter the DataFrame for rows containing any of the Syariah values
                        syariah_df = df[df.iloc[:, 3].isin(syariah_values)]

                        # If there are any Syariah rows, write them to9 the 'Syariah' folder
      
                        syariah_df.to_csv(os.path.join(syariah_folder, filename), index=False)

                        # Filter the DataFrame for rows not containing any of the Syariah values
                        non_syariah_df = df[~df.iloc[:, 3].isin(syariah_values)]
                        non_syariah_df.to_csv(os.path.join(non_syariah_folder, filename), index=False)

            if dialog.fs165:
                syariah_folder = os.path.join(source_folder, "Syariah")
                non_syariah_folder = os.path.join(source_folder, "Non Syariah")
                # Create the 'Syariah' and 'Non Syariah' folders if they do not exist
                os.makedirs(syariah_folder, exist_ok=True)
                os.makedirs(non_syariah_folder, exist_ok=True)

                # List of values to filter on
                syariah_values = [
                    'Syariah Policyholder Fund',
                    'Syariah Shareholder Fund',
                    'Syariah Unitlink Fund'
                ]

                # Process each file
                for filename in os.listdir(source_folder):
                    if filename.endswith('.csv'):
                        print(f"Processing Data {filename}")
                        file_path = os.path.join(source_folder, filename)
                        df = pd.read_csv(file_path, encoding= 'utf-8-sig', dtype=str, keep_default_na=False, na_values=[''], low_memory=False)

                        # Filter the DataFrame for rows containing any of the Syariah values
                        syariah_df = df[df['Fund_group'].isin(syariah_values)]

                        # If there are any Syariah rows, write them to9 the 'Syariah' folder
                        if not syariah_df.empty:
                            syariah_df.to_csv(os.path.join(syariah_folder, filename), index=False)

                        # Filter the DataFrame for rows not containing any of the Syariah values
                        non_syariah_df = df[~df['Fund_group'].isin(syariah_values)]
                        non_syariah_df.to_csv(os.path.join(non_syariah_folder, filename), index=False)

            print("Done!")
            messagebox.showinfo("Info", f"Done Processing.")                        
        else:
            return
   
    def hdr_updater(self):
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the Folder first.")
            return

        hdr_update_option = messagebox.askyesno("HDR Updater", "This will create/replace new hdr based on current FS06 files. Continue?")
        if hdr_update_option:
            csv_directory = self.directory
            dialog = FSDialog(self.master)
            if dialog.fs06:

                def calculate_totals(csv_file_path):
                    df = pd.read_csv(csv_file_path)
                    total_rows = len(df)  
                    total_amount_F = df.iloc[:, 5].sum()  
                    return total_rows, total_amount_F


                for filename in os.listdir(csv_directory):
                    if filename.endswith('.csv'):  
                        print(f"Processing {filename}")
                        csv_file_path = os.path.join(csv_directory, filename)
                        
                        # Calculate totals
                        total_rows, total_amount_F = calculate_totals(csv_file_path)
                        
                        # Convert column index 5 to float64
                        df = pd.read_csv(csv_file_path)
                        df.iloc[:, 5] = df.iloc[:, 5].astype('float64')
                        
                        # Extract information from the CSV file name
                        file_name_parts = os.path.splitext(filename)[0].split('_')
                        country = file_name_parts[1] 
                        system_name = file_name_parts[2]  
                        date_str = file_name_parts[4]  
                        

                        date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"
                        

                        threshold = 1e-10

                        if abs(total_amount_F) < threshold:
                            total_amount_F = 0.0
                        

                        total_amount_F_str_with_commas = '{:,.5f}'.format(total_amount_F)
                        
                
                        total_amount_F_str = total_amount_F_str_with_commas.replace(',', '')
                        
                        hdr_content = f"{country},{system_name},{date},{total_rows},{total_amount_F_str}"
                        

                        hdr_file_path = os.path.join(csv_directory, f"{os.path.splitext(filename)[0]}.hdr")
                        with open(hdr_file_path, 'w') as hdr_file:
                            hdr_file.write(hdr_content)

            if dialog.fs165:
                def calculate_totals(csv_file_path):
                    df = pd.read_csv(csv_file_path)
                    total_rows = len(df)  
                    total_amount_F = df.iloc[:, 9].sum()  
                    return total_rows, total_amount_F


                for filename in os.listdir(csv_directory):
                    if filename.endswith('.csv'):  
                        print(f"Processing {filename}")
                        csv_file_path = os.path.join(csv_directory, filename)
                        
                        # Calculate totals
                        total_rows, total_amount_F = calculate_totals(csv_file_path)
                        
                        # Convert column index 5 to float64
                        df = pd.read_csv(csv_file_path)
                        df.iloc[:, 9] = df.iloc[:, 9].astype('float64')
                        
                        # Extract information from the CSV file name
                        file_name_parts = os.path.splitext(filename)[0].split('_')
                        country = file_name_parts[0] 
                        system_name = file_name_parts[1]  
                        date_str = file_name_parts[2]  
                        

                        date = f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"
                        

                        threshold = 1e-10

                        if abs(total_amount_F) < threshold:
                            total_amount_F = 0.0
                        

                        total_amount_F_str_with_commas = '{:,.5f}'.format(total_amount_F)
                        
                
                        total_amount_F_str = total_amount_F_str_with_commas.replace(',', '')
                        
                        hdr_content = f"{country},{system_name},{date},{total_rows},{total_amount_F_str}"
                        

                        hdr_file_path = os.path.join(csv_directory, f"{os.path.splitext(filename)[0]}.hdr")
                        with open(hdr_file_path, 'w') as hdr_file:
                            hdr_file.write(hdr_content)

            print("HDR files created successfully.")
            messagebox.showinfo("Info", f"HDR Updated.")
        else:
            return
        
    def hdr_compiler(self):

        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the Folder first.")
            return

        hdr_compile_option = messagebox.askyesno("HDR Compile", "This will compile all hdr files in the current folder. Continue?")
        if hdr_compile_option:        
            # Directory where the HDR files are located
            hdr_directory = self.directory

            # Initialize an empty list to store data from HDR files
            hdr_data = []

            # Loop through all HDR files in the directory
            for filename in os.listdir(hdr_directory):
                if filename.endswith('.hdr'):  # Check for HDR files
                    hdr_file_path = os.path.join(hdr_directory, filename)
                    with open(hdr_file_path, 'r') as hdr_file:
                        # Read the content of the HDR file
                        hdr_content = hdr_file.readline().strip().split(',')
                        # Extract the relevant information
                        country = hdr_content[0]
                        file_system = hdr_content[1]
                        date = hdr_content[2]
                        total_rows = float(hdr_content[3])
                        transaction_amount = float(hdr_content[4])
            #             functional_amount = float(hdr_content[5])
                        # Get the file name without extension
                        file_name = os.path.splitext(filename)[0]
                        # Append the extracted information to the list
                        hdr_data.append([country, file_system, date, total_rows, transaction_amount, file_name])

            # Convert the list of lists into a DataFrame
            hdr_df = pd.DataFrame(hdr_data, columns=['Country', 'File System', 'Date','Total Rows', 'Transaction Amount', 'File Name'])

            # Write the DataFrame to an Excel file
            output_excel_file = os.path.join(self.directory, 'compiled_hdr_data.xlsx')
            hdr_df.to_excel(output_excel_file, index=False)

            print("HDR data compiled successfully and saved to", output_excel_file)       
            messagebox.showinfo("Info", f"HDR data compiled successfully and saved to {output_excel_file}") 
        else:
            return
        
    def date_check(self):
        print("Running date fixer...")
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the Folder first.")
            return

        date_fix_option = messagebox.askyesno("Date Fixer", "This will fix date and replace current FS06 files. Continue?")
        if date_fix_option: 
         # Iterate through all files in the FS06 directory
            for filename in os.listdir(self.directory):
                if filename.lower().endswith('.csv'):               
                    filepath = os.path.join(self.directory, filename)
                    date_from_filename = filename.split("_")[4]

                # Check if the file is a CSV and read it into a dataframe
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath, encoding='utf-8-sig', dtype={0: str}, low_memory=False, keep_default_na=False, na_values=[''])
            
            
                # Convert the column to datetime format
                df['Cash Flow Date1'] = pd.to_datetime(df.iloc[:, 12], format='%Y/%m/%d', errors='coerce')
                df['Event Date1'] = pd.to_datetime(df.iloc[:, 11], format='%Y/%m/%d', errors='coerce')            
                
                # Extract the day, month, and year
                df['day'] = df['Cash Flow Date1'].dt.day
                df['month'] = df['Cash Flow Date1'].dt.month
                df['year'] = df['Cash Flow Date1'].dt.year
                
                df['day2'] = df['Event Date1'].dt.day
                df['month2'] = df['Event Date1'].dt.month
                df['year2'] = df['Event Date1'].dt.year

                ed_month = df['Event Date1'].dt.month
                ed_day = df['Event Date1'].dt.day

                # Split the year, month, and day from the filename
                year, month, day = int(date_from_filename[:4]), int(date_from_filename[4:6]), int(date_from_filename[6:])

                # Mark the rows where the cash flow date is less than or equal to the filename date

                cf_below_year = df['year'] < year
                ed_below_year = df['year2'] < year
                cf_above_filename = (df['year'] > year) | ((df['year'] == year) & ((df['month'] > month) | ((df['month'] == month) & (df['day'] > day))))
                ed_above_filename = (df['year2'] > year) | ((df['year2'] == year) & ((df['month2'] > month) | ((df['month2'] == month) & (df['day2'] > day))))
                ed_above_filename_year = df['year2'] > year
                ed_error = df[df['year2'] > year]                

                # Condition 1 - Both CF and ED are below filename year
                both_below_year = cf_below_year & ed_below_year
                df.loc[both_below_year, df.columns[12]] = pd.to_datetime(f'01/01/{year}').strftime('%Y/%m/%d')
                df.loc[both_below_year, df.columns[11]] = pd.to_datetime(f'01/01/{year}').strftime('%Y/%m/%d')

                # Condition 2 - Both CF and ED are above filename date
                both_above_filename = cf_above_filename & ed_above_filename
                df.loc[both_above_filename, df.columns[12]] = pd.to_datetime(f'{year}-{month:02d}-{day:02d}').strftime('%Y/%m/%d')
                df.loc[both_above_filename, df.columns[11]] = pd.to_datetime(f'{year}-{month:02d}-{day:02d}').strftime('%Y/%m/%d')
                
                # Condition 3
                mask3 = cf_below_year & (df['year2'] == year)
                df.loc[mask3, df.columns[12]] = pd.to_datetime(f'01/01/{year}').strftime('%Y/%m/%d')

                # Condition 4
                # Adjust this line to only replace the year while keeping the day and month
                df.loc[ed_above_filename_year, df.columns[11]] = df.loc[ed_above_filename_year, 'Event Date1'].apply(
                    lambda x: x.replace(year=year) if pd.notnull(x) else x
                ).dt.strftime('%Y/%m/%d')

                
                
                # Count the number of False conditions
                countFalse = both_below_year.sum() + both_above_filename.sum() + mask3.sum() + ed_above_filename_year.sum()

                print(f"Total rows with False conditions in {filename}: {countFalse}")

                    # Save the corrected data back to the original file
                df.drop(columns=['Cash Flow Date1', 'day', 'month', 'year'
                                , 'day2', 'month2', 'year2', 'Event Date1'], inplace=True)
    #             df.drop(columns=['Cash Flow Date', 'day', 'month', 'year'], inplace=True)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')

            print("All Date fixed!")        
            messagebox.showinfo("Info", "All Date Fixed!") 

    def fac_reader(self):
        fac_option = messagebox.askyesno("FAC Convert", "This button to convert file FAC to XLSB. Continue ?")
        if fac_option:
            fac_file_path = filedialog.askopenfilename(title="Select the FAC file", filetypes=[("FAC Files", "*.fac")])
            if fac_file_path:
                directory_path = os.path.dirname(fac_file_path)
                # return fac_path, directory_path
            else:
                print("cancelled")
                return

            dialog = FACSplitDialog(self.master)

            messagebox.showinfo("This would be a complex process, please wait", "The process duration depends on how big the FAC file is. \nOnce finished, a message pop up will appear")

            if dialog.sheet:
                # Define the paths
                # fac_file_path, directory_path = select_fac_file()
                print("loading the FAC file...")
                base_name = os.path.splitext(os.path.basename(fac_file_path))[0]
                csv_file_path = os.path.join(directory_path, f'{base_name}.csv')

                # Read the FAC file, clean data, and write to CSV
                data = []
                with open(fac_file_path, 'r') as fac_file:
                    # Skip the first three rows
                    for _ in range(3):
                        next(fac_file)
                    
                    for line in fac_file:
                        # Remove leading and trailing double quotes and commas within quotes using regex
                        cleaned_line = re.sub(r'^"|"$', '', line.strip()).split(',')
                        # Append the cleaned data to the list
                        data.append(cleaned_line)

                # Convert the list to DataFrame to remove the first column
                df = pd.DataFrame(data)
                # Remove the first column
                df.drop(df.columns[0], axis=1, inplace=True)

                # Write the cleaned DataFrame to CSV
                df.to_csv(csv_file_path, index=False, header=False)
                first_csv_path = csv_file_path

                print("FAC file has been loaded to CSV.")

                # Path to the input CSV file and output XLSB file
                xlsb_file_path = os.path.join(directory_path, f'{base_name}.xlsb')
                xlsb_file_path = os.path.normpath(xlsb_file_path)
                temp_excel_path = os.path.join(directory_path, 'temp_output.xlsx')
                # print(xlsb_file_path)

                # Ensure the CSV file exists
                if not os.path.exists(csv_file_path):
                    raise FileNotFoundError(f"No such file or directory: '{csv_file_path}'")

                print("Processing to XLSB...")
                    
                # Read the CSV file into a DataFrame
                df = pd.read_csv(csv_file_path, low_memory=False)
                
                # Define the maximum rows per sheet
                max_rows = 1_000_000

                # Function to split the DataFrame into chunks
                def split_dataframe(df, chunk_size):
                    chunks = []
                    for i in range(0, df.shape[0], chunk_size):
                        chunks.append(df.iloc[i:i + chunk_size])
                    return chunks

                # Check the number of rows and split if necessary
                if len(df) > max_rows:
                    df_chunks = split_dataframe(df, max_rows)
                else:
                    df_chunks = [df]

                # Write each chunk to a separate sheet in a temporary Excel file using xlsxwriter
                with pd.ExcelWriter(temp_excel_path, engine='xlsxwriter') as writer:
                    for i, chunk in enumerate(tqdm(df_chunks, desc="XLSB Writing... (this may take a while)", unit="sheet")):
                        chunk.to_excel(writer, sheet_name=f'Sheet{i+1}', index=False)
                print("Finishing the output...")
                        
                # Convert the temporary Excel file to XLSB using Excel via COM
                excel = win32.gencache.EnsureDispatch('Excel.Application')
                excel.DisplayAlerts = False
                try:
                    wb = excel.Workbooks.Open(temp_excel_path)
                    wb.SaveAs(xlsb_file_path, FileFormat=50)  # 50 is the FileFormat for XLSB
                    wb.Close()
                    print("XLSB file saved successfully")
                finally:
                    excel.Application.Quit()

                print("Removing the temp file...")
                # Ensure the Excel process is properly closed before attempting to delete the temp file
                time.sleep(5)

                # Clean up the temporary Excel file
                try:
                    os.remove(temp_excel_path)
                    os.remove(csv_file_path)
                    # os.remove(first_csv_path)
                    print("Temporary files removed successfully.")
                except PermissionError:
                    print(f"PermissionError: Could not remove temporary files. Please delete manually: {temp_excel_path}, {csv_file_path}")

                print(f"FAC file has been converted to XLSB successfully to {xlsb_file_path}.")
                messagebox.showinfo("Info", f"FAC file has been converted to XLSB successfully to {xlsb_file_path}")          

            if dialog.file:
                print("Loading the FAC file...")
                base_name = os.path.splitext(os.path.basename(fac_file_path))[0]
                csv_file_path = os.path.join(directory_path, f'{base_name}.csv')
                csv_file_path = os.path.normpath(csv_file_path)

                # Read the FAC file, clean data, and write to CSV
                data = []
                with open(fac_file_path, 'r') as fac_file:
                    # Skip the first three rows
                    # Read and store the header
                    header = next(fac_file).strip().split(',')
                    header = [re.sub(r'^"|"$', '', col) for col in header]
                    # Skip the next two rows
                    next(fac_file)
                    next(fac_file)
                    
                    for line in fac_file:
                        # Remove leading and trailing double quotes and commas within quotes using regex
                        cleaned_line = re.sub(r'^"|"$', '', line.strip()).split(',')
                        # Append the cleaned data to the list
                        data.append(cleaned_line)

                # Convert the list to DataFrame to remove the first column
                df = pd.DataFrame(data)
                # Remove the first column
                df.drop(df.columns[0], axis=1, inplace=True)

                # Write the cleaned DataFrame to CSV
                df.to_csv(csv_file_path, index=False, header=False)
                first_csv_path = csv_file_path

                print("FAC file has been loaded to CSV.")

                # Path to the input CSV file and output XLSB file
                xlsb_file_path = os.path.join(directory_path, f'{base_name}.xlsb')
                xlsb_file_path = os.path.normpath(xlsb_file_path)
                temp_excel_path = os.path.join(directory_path, 'temp_output.xlsx')

                # Ensure the CSV file exists
                if not os.path.exists(csv_file_path):
                    raise FileNotFoundError(f"No such file or directory: '{csv_file_path}'")

                print("Processing to XLSB...")

                # Read the CSV file into a DataFrame
                df = pd.read_csv(csv_file_path, low_memory=False)

                # Store the original header
                header = list(df.columns)

                # Define the maximum rows per sheet
                max_rows = 1_000_000

                def save_to_xlsb(csv_file_path, xlsb_file_path):
                    # Ensure the CSV file exists
                    if not os.path.exists(csv_file_path):
                        raise FileNotFoundError(f"No such file or directory: '{csv_file_path}'")

                    print(f"Processing {csv_file_path} to XLSB...")

                    # Read the CSV file into a DataFrame
                    df = pd.read_csv(csv_file_path, low_memory=False)

                    # Write the DataFrame to a temporary Excel file using xlsxwriter
                    temp_excel_path = csv_file_path.replace('.csv', '_temp.xlsx')
                    with pd.ExcelWriter(temp_excel_path, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name='Sheet1', index=False)
                    print("Almost done...")

                    # Convert the temporary Excel file to XLSB using Excel via COM
                    excel = win32.gencache.EnsureDispatch('Excel.Application')
                    excel.DisplayAlerts = False  # Disable any prompts
                    try:
                        wb = excel.Workbooks.Open(temp_excel_path)
                        wb.SaveAs(xlsb_file_path, FileFormat=50)  # 50 is the FileFormat for XLSB
                        wb.Close()
                        print(f"XLSB file {xlsb_file_path} saved successfully.")
                    finally:
                        excel.Application.Quit()

                    # Clean up the temporary Excel file
                    try:
                        os.remove(temp_excel_path)
                        print(f"Temporary file {temp_excel_path} removed successfully.")
                    except PermissionError:
                        print(f"PermissionError: Could not remove temporary file. Please delete manually: {temp_excel_path}")

                # Function to split the DataFrame into chunks
                def split_dataframe(df, chunk_size):
                    chunks = []
                    for i in range(0, df.shape[0], chunk_size):
                        chunks.append(df.iloc[i:i + chunk_size])
                    return chunks

                # Split the DataFrame into chunks
                df_chunks = split_dataframe(df, max_rows)

                # Write each chunk to a CSV file with the original header
                csv_files = []
                for i, chunk in enumerate(df_chunks):
                    chunk_file_path = os.path.join(directory_path, f'{base_name}_part{i+1}.csv')
                    chunk.to_csv(chunk_file_path, index=False, header=header)
                    csv_files.append(chunk_file_path)
                    print(f"CSV part {i+1} saved to {chunk_file_path}")

                # Convert each CSV file to XLSB
                for csv_file_path in csv_files:
                    xlsb_file_path = csv_file_path.replace('.csv', '.xlsb')
                    xlsb_file_path = os.path.normpath(xlsb_file_path)
                    save_to_xlsb(csv_file_path, xlsb_file_path)

                # Clean up the CSV files
                os.remove(first_csv_path)
                for csv_file_path in csv_files:
                    try:
                        os.remove(csv_file_path)
                        print(f"CSV file {csv_file_path} removed successfully.")
                    except PermissionError:
                        print(f"PermissionError: Could not remove CSV file. Please delete manually: {csv_file_path}")

                print("All CSV files have been converted to XLSB successfully.")
                messagebox.showinfo("Info", f"FAC file has been converted to XLSB successfully to {directory_path}")
        else:
            return
        
    def csv_split(self):
        csv_split_option = messagebox.askyesno("CSV Split", "This button is to split a big file CSV into mini parts. Continue?")
        if csv_split_option:
            csv_path = filedialog.askopenfilename(title="Select the CSV file", filetypes=[("CSV Files", "*.csv")])
            if csv_path:
                directory_path = os.path.dirname(csv_path)
                # return fac_path, directory_path
            else:
                print("cancelled")
                return
            
            user_input = simpledialog.askinteger("Input Number","Input max rows per file")
            try:
                chunk_size = int(user_input)
            except ValueError:
                print("Your input is not a number, please try again")

            chunk_generator = pd.read_csv(csv_path, chunksize=chunk_size, encoding='utf-8-sig', dtype=str, keep_default_na=False, na_values=[''] )
        
            base_name = os.path.basename(csv_path)
            file_name = os.path.splitext(base_name)[0]

            for i, chunk in enumerate(chunk_generator):
                chunk.to_csv(f'{directory_path}/{file_name} Part {i+1}.csv', index=False)
                print(f"New csv part saved to {directory_path}/{file_name} Part {i+1}.csv")

            messagebox.showinfo("Info", f"CSV file has been splitted successfully to {directory_path}")  

if __name__ == "__main__":
    root = tk.Tk()
    app = DataManager(root)
    root.mainloop()
