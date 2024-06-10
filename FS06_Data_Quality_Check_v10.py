import tkinter as tk
from tkinter import filedialog, Label, Button
import os
import pandas as pd
import numpy as np
import time
from datetime import datetime
import xlsxwriter
from tkinter.simpledialog import Dialog
from tkinter import filedialog, simpledialog, messagebox, Label
from tkinter import ttk


class DataQualityChecker(tk.Tk):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initialize()
        self.grouped_df = None
        self.date_error = False
        self.proposal_error = False
        self.missing_policy = False
        self.blank_policy_number = False
        self.blank_account_code_event_code = False
        self.missing_account_map = False
        self.missing_fs10 = False
        self.list_acf_credit_life_policy = False
        self.non_idr = False
        
    def initialize(self):
        self.grid()

        # Styles and Utilities
        self.bg_color = "#282c34"  # Dark background color
        self.text_color = "#a9b7c6"  # Light text color
        self.highlight_color = "dark orange"
        self.configure(bg=self.bg_color)
        self.create_styles()
        self.create_gui_elements()
        


    def create_styles(self):
        # Create a style for the checkbuttons to match the background
        style = ttk.Style()
        style.configure("Custom.TCheckbutton",
                        background=self.bg_color,
                        foreground=self.text_color,
                        font=("Calibri", 12))
        style.map("Custom.TCheckbutton",
                  background=[('active', self.bg_color)],
                  foreground=[('active', self.text_color)])        

    def create_gui_elements(self):
        
        self.create_label("Please specify your FS02 and FS06 input folders:", 12).grid(row=13, column=0, sticky='w', padx=10, pady=5)

        # Search FS02 Folder Button
        tk.Button(self, text="Search FS02 Folder", command=lambda: self.inputfunc('FS02'), fg="white", bg="red").grid(row=14, column=0, sticky='w', padx=10, pady=5)
        self.fs02_label = self.create_label("", 12)
        self.fs02_label.grid(row=14, column=1)

        # Search FS06 Folder Button
        tk.Button(self, text="Search FS06 Folder", command=lambda: self.inputfunc('FS06'), fg="white", bg="red").grid(row=15, column=0, sticky='w', padx=10, pady=5)
        self.fs06_label = self.create_label("", 12)
        self.fs06_label.grid(row=15, column=1)

        # Select Output Directory Button
        tk.Button(self, text="Select Output Directory", command=self.output_directory, fg="white", bg="blue").grid(row=16, column=0, sticky='w', padx=10, pady=5)
        self.output_label = self.create_label("", 12)
        self.output_label.grid(row=16, column=1)
        
        # Select DPLAPT Lookup File
        tk.Button(self, text="Select DPLAPT_Lookup File", command=self.select_dpl_file, fg="white", bg="purple").grid(row=17, column=0, sticky='w', padx=10, pady=5)
        self.dpl_file_label = self.create_label("", 12)
        self.dpl_file_label.grid(row=17, column=1)


        # Start Data Quality Check Button
        tk.Button(self, text="Start Data Quality Check", command=self.run_checks, fg="white", bg="green").grid(row=18, column=0, sticky='w', padx=10, pady=10, columnspan=2)
        
        self.create_label("Welcome to FS06 Data Quality Checker", 20, self.highlight_color, True).grid(row=1, column=0, sticky='w')
        self.create_label("\nSelect which check to run:", 12).grid(row=2, column=0, sticky='w')

        # Create a frame for checkboxes with the same background color
        checkbox_frame = tk.Frame(self, bg=self.bg_color)
        checkbox_frame.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=5)

        # Add checkboxes
        self.date_error_var = tk.BooleanVar()
        self.proposal_error_var = tk.BooleanVar()
        self.missing_policy_var = tk.BooleanVar()
        self.blank_policy_number_var = tk.BooleanVar()
        self.blank_account_code_event_code_var = tk.BooleanVar()
        self.missing_account_map_var = tk.BooleanVar()
        self.missing_fs10_var = tk.BooleanVar()
        self.list_acf_credit_life_policy_var = tk.BooleanVar()
        self.non_idr_var = tk.BooleanVar()

        self.create_checkbox(checkbox_frame, "1). Date Error", self.date_error_var).grid(row=0, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "2). Proposal Error", self.proposal_error_var).grid(row=1, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "3). Missing Policy", self.missing_policy_var).grid(row=2, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "4). Blank Policy Number", self.blank_policy_number_var).grid(row=3, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "5). Blank Account Code & Event Code", self.blank_account_code_event_code_var).grid(row=4, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "6). Missing Account MAP", self.missing_account_map_var).grid(row=5, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "7). Missing FS10", self.missing_fs10_var).grid(row=6, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "8). List ACF Credit Life Policy", self.list_acf_credit_life_policy_var).grid(row=7, column=0, sticky='w')
        self.create_checkbox(checkbox_frame, "9). List Non IDR OC=FC", self.non_idr_var).grid(row=8, column=0, sticky='w')


        # Check All button
        tk.Button(self, text="Check All", command=self.check_all).grid(row=8, column=0, sticky='w', padx=10, pady=5)

        # self.create_label("\nPlease pay attention to the following points before inputting your data:", 12).grid(row=7, column=0, sticky='w')
        # self.create_label("1). Make sure that the data you input has 32 columns.", 12).grid(row=8, column=0, sticky='w')
        # self.create_label("2). Make sure all the latest FS02 files has been placed in folder FS02", 12).grid(row=9, column=0, sticky='w')
        # self.create_label("3). Output directory must be different from both FS02 or FS06 folder path.", 12).grid(row=11, column=0, sticky='w')
        # self.create_label("4). Only CSV files are allowed in the FS06 folder.\n", 12).grid(row=12, column=0, sticky='w')

    def create_checkbox(self, master, text, variable):
        checkbox = ttk.Checkbutton(master, text=text, variable=variable, style="Custom.TCheckbutton")
        return checkbox 
        
    def create_label(self, text, font_size, color=None, bold=False):
        color = color or self.text_color
        font_style = "bold" if bold else "normal"
        label = Label(self, text=text, font=("Calibri", font_size, font_style), fg=color, bg=self.bg_color)
        return label
    
    def check_all(self):
        current_state = self.date_error_var.get()
        new_state = not current_state
        
        self.date_error_var.set(new_state)
        self.proposal_error_var.set(new_state)
        self.missing_policy_var.set(new_state)
        self.blank_policy_number_var.set(new_state)
        self.blank_account_code_event_code_var.set(new_state)
        self.missing_account_map_var.set(new_state)
        self.missing_fs10_var.set(new_state)
        self.list_acf_credit_life_policy_var.set(new_state)
        self.non_idr_var.set(new_state)

    def select_dpl_file(self):
        self.dpl_lookup_path = filedialog.askopenfilename(title="Select the DPLAPT_Lookup File", filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        if self.dpl_lookup_path:
            self.directory_path = os.path.dirname(self.dpl_lookup_path)
            self.dpl_file_label['text'] = f"DPL_LOOKUP File: {os.path.basename(self.dpl_lookup_path)}"
        else:
            print("No file selected.")

             
    def inputfunc(self, fileType):
        path = filedialog.askdirectory()
        if fileType == 'FS02':
            self.fs02_label['text'] = f"Your {fileType} folder: {path}"
            self.fs02path = path
        else:
            self.fs06_label['text'] = f"Your {fileType} folder: {path}"
            self.fs06path = path
            
            
    def merge_with_dpl(self, df):
        if not hasattr(self, 'dpl_lookup_path') or not self.dpl_lookup_path:
            print("Please select the DPL_LOOKUP file first.")
            return df

        # Read the specific sheet while ensuring 'NA' is not treated as NaN
        dpl = pd.read_excel(self.dpl_lookup_path, sheet_name='DPL_CF_TYPE_ACCOUNT_MAP', keep_default_na=False, na_values=[''])

        dpl['LK_MATCH_KEY2'] = dpl['LK_MATCH_KEY2'].replace('~ND', 'ZND')
        dpl = dpl.sort_values(
                    by=["LK_MATCH_KEY4", "LK_MATCH_KEY2", "LK_MATCH_KEY5"],
                    ascending=[False, True, True] 
                )
        dpl['LK_MATCH_KEY2'] = dpl['LK_MATCH_KEY2'].replace('ZND', '~ND')

        df['composite_key'] = df[df.columns[10]].astype(str) + df[df.columns[9]].astype(str)
        dpl['composite_key'] = dpl['LK_MATCH_KEY4'].astype(str) + dpl['LK_MATCH_KEY2'].astype(str)

        dpl.drop_duplicates(subset= 'composite_key', inplace=True)

        # Merge using the new composite key
        merged_df = pd.merge(df, dpl[['LK_LOOKUP_VALUE1', 'composite_key']], on='composite_key', how='left')

        # Rename the column
        merged_df.rename(columns={'LK_LOOKUP_VALUE1': 'Cash Flow Type'}, inplace=True)

        # Drop the composite key columns
        merged_df.drop(columns=['composite_key'], inplace=True)

        return merged_df
  
    
    def output_directory(self):
        output_path = filedialog.askdirectory()
        if output_path:  # If a path was selected
            print(f"You've selected the directory: {output_path}")
            self.output_label['text'] = f"Output Directory: {output_path}"
            self.selected_output_path = output_path
        else:  # If no path was selected (i.e., user canceled the dialog)
            print("No directory selected. Using default location.")
            self.selected_output_path = os.getcwd()  # Store the current working directory as default 


    
    def date_check(self, df, date_from_filename):
        print("Running event date & CF date check...")

        new_df = df.copy()
        new_df['Cash Flow Date1'] = pd.to_datetime(new_df.iloc[:, 12], format='%Y/%m/%d', errors='coerce')
        new_df['Event Date1'] = pd.to_datetime(new_df.iloc[:, 11], format='%Y/%m/%d', errors='coerce')            

        # Extract the day, month, and year
        new_df['day'] = new_df['Cash Flow Date1'].dt.day
        new_df['month'] = new_df['Cash Flow Date1'].dt.month
        new_df['year'] = new_df['Cash Flow Date1'].dt.year

        new_df['day2'] = new_df['Event Date1'].dt.day
        new_df['month2'] = new_df['Event Date1'].dt.month
        new_df['year2'] = new_df['Event Date1'].dt.year

        year, month, day = int(date_from_filename[:4]), int(date_from_filename[4:6]), int(date_from_filename[6:])

        cf_below_year = new_df['year'] < year
        ed_below_year = new_df['year2'] < year
        cf_above_filename = (new_df['year'] > year) | ((new_df['year'] == year) & ((new_df['month'] > month) | ((new_df['month'] == month) & (new_df['day'] > day))))
        ed_above_filename = (new_df['year2'] > year) | ((new_df['year2'] == year) & ((new_df['month2'] > month) | ((new_df['month2'] == month) & (new_df['day2'] > day))))
        
        both_below_year = cf_below_year & ed_below_year
        both_above_filename = cf_above_filename & ed_above_filename        
        mask3 = cf_below_year & (new_df['year2'] == year)
        
        date_errors = both_below_year.sum() + both_above_filename.sum() + mask3.sum()
        return date_errors
    
    def blanks_check(self, df, filename):
        if not hasattr(self, 'directory_path') or not self.directory_path:
            print("Please select the DPL_LOOKUP file first.")
            return df
        
        print("Running blanks Policy Number check...")
        
        coapath = os.path.join(self.directory_path, 'List ACF CoA for DQ Blank Policy.xlsx')
        coa = pd.read_excel(coapath, dtype=str)
        # print(coa.shape)
        # coa = coa.drop_duplicates(subset='Account Code')
        # print(coa.shape)
        merged_data = pd.DataFrame()
        new_df = df.copy()
        # grouped_df2 = self.grouped_df
        new_df[new_df.columns[1]] = new_df[new_df.columns[1]].astype(str)
        new_df[new_df.columns[10]] = new_df[new_df.columns[10]].astype(str) 
        
        # Filter rows where the column at index 1 (i.e., 'Policy Number') is either NaN or blank
        # new_df[new_df.columns[1]] = new_df[new_df.columns[1]].fillna("NULL")
        df_filtered = new_df[(new_df.iloc[:, 1].isna()) | (new_df.iloc[:, 1] == 'NULL')]
        
        if not df_filtered.empty:

            merged_data = pd.merge(df_filtered, coa['Account Code'], left_on=df_filtered.columns[10], right_on='Account Code', how = 'inner')
#             merged_data.drop(merged_data.columns[13:41], axis=1, inplace=True)
            merged_data.drop(merged_data.columns[13:31], axis=1, inplace=True)
            merged_data.drop_duplicates(inplace=True)
            merged_data['File Name'] = filename

        blanks_count = len(merged_data)
                
        return blanks_count, merged_data
    
    def blank_code_check(self, df, filename):
        print("Running blank Event Code & Account Code check...")
        
        df_filtered = df[(df.iloc[:, 9].isna() | (df.iloc[:, 9] == 'NULL')) | (df.iloc[:, 10].isna() | (df.iloc[:, 10] == 'NULL'))]

        if not df_filtered.empty:

            df_filtered.drop(df_filtered.columns[13:41], axis=1, inplace=True)
            df_filtered.drop_duplicates(inplace=True)
            df_filtered['File Name'] = filename
        
        blank_code_count = len(df_filtered)
        return blank_code_count, df_filtered
    
    def dpl_key_check(self, df, filename):
        if not hasattr(self, 'dpl_lookup_path') or not self.dpl_lookup_path:
            print("Please select the DPL_LOOKUP file first.")
            return df

        print("Running Missing Account MAP check...")
        # Read the specific sheet while ensuring 'NA' is not treated as NaN
        dpl = pd.read_excel(self.dpl_lookup_path, sheet_name='DPL_CF_TYPE_ACCOUNT_MAP', keep_default_na=False, na_values=[''])

        new_df = df.copy()

        # Concatenate the columns in both DataFrames to form the composite keys
        parts = filename.split('_')
        second_text = parts[2]
        new_df['File System'] = second_text
        new_df[new_df.columns[10]] = new_df[new_df.columns[10]].astype(str)
        new_df[new_df.columns[9]] = new_df[new_df.columns[9]].astype(str)

        new_df[new_df.columns[9]] = new_df[new_df.columns[9]].replace('ND~', 'ND')
        dpl['LK_MATCH_KEY2'] = dpl['LK_MATCH_KEY2'].replace('ND~', 'ND')

        new_df['composite_key_data'] = new_df['File System'].astype(str) + new_df[new_df.columns[10]].astype(str) + new_df[new_df.columns[9]].astype(str)
        dpl['composite_key_dpl'] = dpl['LK_MATCH_KEY3'].astype(str) + dpl['LK_MATCH_KEY4'].astype(str) + dpl['LK_MATCH_KEY2'].astype(str)

        # Merge using the new composite key
        merged_df = pd.merge(new_df, dpl['composite_key_dpl'], left_on= 'composite_key_data', right_on= 'composite_key_dpl', how='left')

        merged_df['File Name'] = filename

        # Drop duplicates based on the original column in df


        missing_key = merged_df[merged_df['composite_key_dpl'].isnull()]
        missing_key = missing_key.drop_duplicates(subset='composite_key_data')       
        missing_key_count = len(missing_key)
        
        missing_key.drop(missing_key.columns[13:41], axis=1, inplace=True)

        return missing_key, missing_key_count
    
    def credit_life_policy(self, df, filename):
        if not hasattr(self, 'dpl_lookup_path') or not self.dpl_lookup_path:
            print("Please select the DPL_LOOKUP file first.")
            return df

        print("Gathering Credit Life Policy Data...")

        new_df = df.copy()
            # List of column indices to drop
        indices_to_drop = [0, 2, 4, 8, 13]
        account_code = new_df.columns[10]
        event_code = new_df.columns[9]
        # Adding indices of columns after index 13
        indices_to_drop.extend(range(14, len(new_df.columns)))

        # Drop columns by indices

        
        new_df.drop(new_df.columns[indices_to_drop], axis=1, inplace=True)          

        # Concatenate the columns in both DataFrames to form the composite keys
        parts = filename.split('_')
        second_text = parts[2]
        new_df['Source'] = second_text
        filter = ['MANUAL', 'OFCGL']
        new_df = new_df[new_df['Source'].isin(filter)]
        new_df['Concat ID'] = new_df[account_code].astype(str) + "_" + new_df[event_code].apply(lambda x: "ND" if x == "ND~" else x)
      
        new_df['column_lengths'] = new_df[new_df.columns[0]].astype(str).apply(len)
        clp = new_df[new_df['column_lengths'] > 8]
        clp.drop('column_lengths', axis=1, inplace=True)

        clp['File Name'] = filename

        # Drop duplicates based on the original column in df

        return clp
        

    def proposal_check(self, df, df02, filename):
        print("Running proposal check...")
        
        new_df = df.copy()
            # List of column indices to drop
        indices_to_drop = [0, 2, 4, 8, 13]

        # Adding indices of columns after index 13
        indices_to_drop.extend(range(14, len(new_df.columns)))

        # Drop columns by indices

        
        new_df.drop(new_df.columns[indices_to_drop], axis=1, inplace=True)
        
        key_col_df = new_df.columns[0]
        key_col_df02 = df02.columns[0]

        new_df[key_col_df] = new_df[key_col_df].astype(str)
        df02[key_col_df02] = df02[key_col_df02].astype(str)

        new_df[new_df.columns[7]] = pd.to_datetime(new_df[new_df.columns[7]], errors='coerce')
        df02[df02.columns[16]] = pd.to_datetime(df02[df02.columns[16]], errors='coerce')

        fs02 = df02.rename(columns={df02.columns[0]: new_df.columns[0]})

        print("STEP 0 EVENT DATE FIX")
        start_time = time.time()    

        # Find the earliest Coverage Start Date for each Policy Number
        earliest_dates = fs02.groupby(key_col_df)[fs02.columns[16]].min().reset_index()

        # Merge the new_df dataframe with the earliest dates dataframe
        merged_df = new_df.merge(earliest_dates, on=key_col_df, how='left')

        # Update the EventDate in new_df where it is before the earliest Coverage Start Date
        merged_df.loc[merged_df[new_df.columns[7]] < merged_df[fs02.columns[16]], new_df.columns[7]] = merged_df[fs02.columns[16]]

        new_df = merged_df.drop(fs02.columns[16], axis=1)
        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")

        if not key_col_df02.endswith('for check'):
            df02.rename(columns={key_col_df02: key_col_df02 + ' for check'}, inplace=True)
            key_col_df02 = key_col_df02 + ' for check'
      
        new_df[new_df.columns[2]] = new_df[new_df.columns[2]].astype(float)
        new_df[new_df.columns[4]] = new_df[new_df.columns[4]].astype(float)
        
#         my_id = '64060633'

#         filtered_df = new_df[new_df['PolicyNumber'] == my_id]
#         print(filtered_df)
        
        print("STEP 1 FILL MISSING")
        start_time = time.time()       
        new_df = new_df.fillna('Missing')
        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")
        
        
        print("STEP 2 AGG")
        start_time = time.time()  
        grouped_df = new_df.groupby([new_df.columns[0], new_df.columns[6], new_df.columns[7]], as_index=False).agg({col: 'last' if col not in [new_df.columns[2], new_df.columns[4]] else 'sum' for col in new_df.columns})#.astype({df_updated.columns[5]: float, df_updated.columns[7]: float})
        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")
        
#         filtered_df = grouped_df[grouped_df['PolicyNumber'] == my_id]
#         print(filtered_df)       
        
        print("STEP 3 REPLACE MISSING")
        start_time = time.time()        
        grouped_df = grouped_df.replace('Missing', np.nan)
        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")        
        self.grouped_df = grouped_df

        
        print("STEP 4 MERGE")
        start_time = time.time()     
        # Merge the dataframes
        merged_df = pd.merge(grouped_df, df02[[key_col_df02, df02.columns[4], df02.columns[16], 'FS02 File Name']], left_on=key_col_df, right_on=key_col_df02, how='left')
#         merged_df.drop(merged_df.columns[13:30], axis=1, inplace=True)
        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")
#         print("merged df1")
#         merged_df.info()

        # Extracting rows where the date condition is met

        print("STEP 5 DATE CHECK")
        start_time = time.time()        
        merged_df['Date Check'] = (pd.to_datetime(merged_df[new_df.columns[7]]) >= pd.to_datetime(merged_df[df02.columns[16]])).map({True: 'Yes', False: 'No'})

        merged_df.drop_duplicates(inplace=True)

        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")         
        

        # Filtering rows with 'Date Check' equals 'Yes'
        merged_df = merged_df[merged_df['Date Check'] == 'Yes']


#             Check if updated_df is empty
        if merged_df.empty:
            print("updated_df is empty. Skipping processing.")
            return 0, pd.DataFrame()  # Return 0 errors and an empty DataFrame
#         print("data merged 2")
#         merged_df.info()

        print("STEP 6 SORT DATE")
        start_time = time.time()        
        # Sorting by date and keeping only the latest row for each ID
        updated_df = merged_df.sort_values(by= merged_df.columns[11], ascending=True, kind='mergesort')
        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")
        
        print("STEP 7 APPLY LAST")
        start_time = time.time()        
#         def apply_last(group):
#             if group[group.columns[10]].nunique() > 1:
#                 return group.tail(1)  # Apply last() if different PolicyStatus values
#             return group  # Keep all rows if PolicyStatus values are the same

        # Apply the function to each group of ['PolicyNumber', 'AccountCode', 'EventDate']

        updated_df = updated_df.groupby([updated_df.columns[0], updated_df.columns[6], updated_df.columns[7]], as_index=False).last()

        # Reset the index if needed
        updated_df.reset_index(drop=True, inplace=True)
        end_time = time.time()
        duration = end_time - start_time
        print(f"The process took {duration} seconds.")
        
#         print("data merged 3")
#         updated_df.info()
        


        error_values = ['DC|PS', 'NT|PS', 'PO|PS', 'PS|PS', 'WD|PS', 'AP|PP', 'AP|SP', 'AP|HA', 'MP|PP', 'MP|HA', 'UW|PS']
        proposal_errors = updated_df[updated_df[df02.columns[4]].isin(error_values)]
        proposal_errors['File Name'] = filename

        # Drop duplicates based on the original column in df
#         proposal_errors = proposal_errors.drop_duplicates(subset=[key_col_df, merged_df.columns[11], merged_df.columns[10], merged_df.columns[42]])
        proposal_errors = proposal_errors[~proposal_errors[key_col_df].isin(['NULL', ''])]
#         print("data proposal")
#         proposal_errors.info()
#         proposal_errors.drop(proposal_errors.columns[11:24], axis=1, inplace=True)
#         print("dropped proposal")
#         proposal_errors.info()

        proposal_error_count = len(proposal_errors)

        return proposal_error_count, proposal_errors


#     def out_date_check(self, df, df02, filename):
#         print("Running out date check...")
#         merged_df = pd.merge(df, df02[['ZXPOLNUM', 'ZXPSTDTE']], left_on=df.columns[1], right_on='ZXPOLNUM', how='left')
#         merged_df['ZXPSTDTE'] = pd.to_datetime(merged_df['ZXPSTDTE'])
#         out_date_errors = merged_df[merged_df.iloc[:, 11] < merged_df['ZXPSTDTE']]
#         out_date_errors['File Name'] = filename
#         out_date_count = len(out_date_errors)

#         return out_date_count, out_date_errors

    def missing_policy_check(self, df, df02, filename):
        print("Running missing policy check...")
        
        # Assuming df02 is defined elsewhere in your code
        new_df2 = df.copy()
        # num_rows, num_columns = new_df2.shape
        # print("Number of rows:", num_rows)
        # print("Number of columns:", num_columns)

            # List of column indices to drop
        indices_to_drop = [0, 2, 4, 8, 13]

        # Adding indices of columns after index 13
        indices_to_drop.extend(range(14, len(new_df2.columns)))

        # Drop columns by indices

        print("STEP 1: Drop Columns...")
        new_df2.drop(new_df2.columns[indices_to_drop], axis=1, inplace=True)
        
        key_col_df = new_df2.columns[0]
        key_col_df02 = df02.columns[0]

        print("STEP 2: Rename column key and drop duplicates")
        if not key_col_df02.endswith('for check'):
            df02.rename(columns={key_col_df02: key_col_df02 + ' for check'}, inplace=True)
            key_col_df02 = key_col_df02 + ' for check'
            
        df02 = df02.drop_duplicates(subset=df02.columns[0], keep='last').reset_index(drop=True)    
        
        new_df2[key_col_df] = new_df2[key_col_df].astype(str)
        df02[key_col_df02] = df02[key_col_df02].astype(str)
        print("STEP 3: Merging df..")
        # num_rows, num_columns = new_df2.shape
        # print("Number of rows df:", num_rows)
        # print("Number of columns df:", num_columns) 
        # num_rows2, num_columns2 = df02.shape
        # print("Number of rows fs02:", num_rows2)
        # print("Number of columns fs02:", num_columns2)         
        
        # Merge the dataframes
        merged_df = pd.merge(new_df2, df02[[key_col_df02]], left_on=key_col_df, right_on=key_col_df02, how='left')

        # Assuming 'filename' is defined elsewhere in your code or you can assign it a specific value
        # e.g., filename = "some_value.csv"

        # Extracting rows where the key from df02 is missing in the merged dataframe
        print("STEP 4: filter null values...")
        missing_policies = merged_df[merged_df[key_col_df02].isnull()]
        missing_policies['File Name'] = filename
        
        print("STEP 5: transform & count values...")
        # Drop duplicates based on the original column in df
        missing_policies = missing_policies.drop_duplicates(subset=key_col_df)
        missing_policies = missing_policies[~missing_policies[key_col_df].isin(['NULL', ''])]
        missing_policies.drop(missing_policies.columns[13:41], axis=1, inplace=True)
        
        missing_count = len(missing_policies)

        return missing_count, missing_policies
    
    def fs0610_check(self, df, fs10, df02copy, filename):
        print("Running FS0610 Check...")
 
        new_df3 = df.copy()     

        if new_df3.empty:
            print("df is empty. Skipping processing.")
            return pd.DataFrame(), 0

        else:
            indices_to_drop = [0,2,4,8,13]
            indices_to_drop.extend(range(14, len(new_df3.columns)-3))

            new_df3.drop(new_df3.columns[indices_to_drop], axis=1, inplace=True)
            new_df3.drop_duplicates(inplace=True)
            parts = filename.split('_')
            second_text = parts[2]
            new_df3['File System'] = second_text

            key_col_df = new_df3.columns[0]
            key_col_fs10 = fs10.columns[0]

            key_col_df02 = df02copy.columns[0]     
            
            if not key_col_df02.endswith('for check'):
                df02copy.rename(columns={key_col_df02: key_col_df02 + ' for check'}, inplace=True)
                key_col_df02 = key_col_df02 + ' for check'                    

            if not key_col_fs10.endswith('FS10'):
                fs10.rename(columns={key_col_fs10: key_col_fs10 + ' FS10'}, inplace=True)
                key_col_fs10 = key_col_fs10 + ' FS10'

            new_df3['File Name'] = filename       
            new_df3['composite_key_data'] = new_df3['File System'].astype(str) + new_df3[new_df3.columns[6]].astype(str) + new_df3[new_df3.columns[5]].astype(str)

            new_df3[key_col_df] = new_df3[key_col_df].astype(str)
            fs10[key_col_fs10] = fs10[key_col_fs10].astype(str)

            merged_df = pd.merge(new_df3, fs10, left_on=key_col_df, right_on=key_col_fs10, how='left')
            missing_fs0610 = merged_df[merged_df[key_col_fs10].isnull()]

            missing_fs0610['concat'] = missing_fs0610['composite_key_data'] + missing_fs0610[missing_fs0610.columns[0]]

            missing_fs0610 = missing_fs0610.drop_duplicates(subset ='concat')
            missing_fs0610 = missing_fs0610[~missing_fs0610[key_col_df].isin(['NULL', ''])]

            missing_fs0610 = missing_fs0610[missing_fs0610['Cash Flow Type'] != 'NA']
            missing_fs0610.drop(missing_fs0610.columns[14:17], axis=1, inplace=True)
  

            missing_fs0610 = pd.merge(missing_fs0610, df02copy[[df02copy.columns[0], df02copy.columns[18]]], left_on=key_col_df, right_on=df02copy.columns[0], how='left')
            # missing_fs0610.drop(missing_fs0610[['concat', 'composite_key_data']], axis=1, inplace=True)
            dpl2 = pd.read_excel(self.dpl_lookup_path, sheet_name='DPL_CONTRACT_STATUS_MAP', keep_default_na=False, na_values=[''])
            missing_fs0610 = pd.merge(missing_fs0610, dpl2[['LK_MATCH_KEY3', 'LK_LOOKUP_VALUE2']], left_on=df02copy.columns[18], right_on='LK_MATCH_KEY3', how='left')
            missing_fs0610 = missing_fs0610.drop(columns=['LK_MATCH_KEY3'])

            missing_fs0610 = missing_fs0610.rename(columns={"LK_LOOKUP_VALUE2": "Status Type"})
            missing_fs0610_count = len(missing_fs0610)

            return missing_fs0610, missing_fs0610_count

    def non_idr_list(self, df, filename):
         print("Gathering non IDR OC=FC...")
         new_df = df.copy()

         new_df["File Name"] = filename
         new_df = new_df[~new_df[new_df.columns[6]].isin(['IDR'])]
         new_df.iloc[:, 5] = new_df.iloc[:, 5].astype(float)
         new_df.iloc[:, 7] = new_df.iloc[:, 7].astype(float)
         # Filter out rows where column 5 is zero
         new_df = new_df[new_df.iloc[:, 5] != 0]
        
         # Divide each row of column 7 by column 5
         new_df["Result"] = new_df.iloc[:, 7] / new_df.iloc[:, 5]
        
         # Filter the result for values <= 1
         non_idr = new_df[new_df["Result"] <= 1]
        
         indices_to_drop = [0,2,4,8,13]
         indices_to_drop.extend(range(14, len(non_idr.columns)-3))
         non_idr.drop(non_idr.columns[indices_to_drop], axis=1, inplace=True)
         non_idr.drop_duplicates(inplace=True)
         non_idr_count = len(non_idr)

         return non_idr, non_idr_count

    def load_fs02_files(self):
        print("Loading FS02 files...")
        # Create an empty list to hold dataframes
        dfs = []
        all_files = sorted([f for f in os.listdir(self.fs02path) if f.endswith('.csv')])

        # Load the header from the first file
        header_file_path = os.path.join(self.fs02path, all_files[0])
        first_file_df = pd.read_csv(header_file_path, encoding='unicode_escape', dtype= str, low_memory=False)
        header = first_file_df.columns.tolist()
        first_file_df['FS02 File Name'] = all_files[0]  # Add new column with file name
        dfs.append(first_file_df)
        print(f"combining {all_files[0]}...")

        # Iterate through the rest of the files in the FS02 directory using the header from the first file
        for filename in all_files[1:]:
            print(f"combining {filename}...")
            filepath = os.path.join(self.fs02path, filename)

            df = pd.read_csv(filepath, encoding='unicode_escape', dtype=str, header=None, names=header)
            df['FS02 File Name'] = filename  # Add new column with file name
            dfs.append(df)

        # Concatenate all dataframes in the list into a single dataframe
        df02 = pd.concat(dfs, ignore_index=True)
        df02copy = df02.copy()

        df02copy = df02copy.sort_values(
            by=[df02copy.columns[0], df02copy.columns[13], "FS02 File Name", df02copy.columns[16], df02copy.columns[19]],
            ascending=[True, False, False, False, True] 
        )
        df02copy = df02copy.drop_duplicates(subset=df02.columns[0]).reset_index(drop=True)    


        # Drop duplicates keeping the last entry and reset index
        # df02 = df02.drop_duplicates(subset=header[0], keep='last').reset_index(drop=True)
        print("FS02 files loaded successfully!")

        return df02, df02copy

    def load_fs10_files(self):
        if self.missing_fs10_var.get():
            print("Loading FS10 files...")
            fs10s = []
            fs10_path = os.path.join(self.directory_path, 'List IF MPF.xlsx')
            first_sheet = pd.read_excel(fs10_path, sheet_name='FWDL', dtype=str)
            header = first_sheet.columns.tolist()
            first_sheet = first_sheet.iloc[:, 0:1]
            first_sheet.drop_duplicates(inplace=True)
            first_sheet.reset_index(drop=True, inplace=True)

            fs10s.append(first_sheet)
            # Read each sheet into separate dataframes
            sheet_names = ['PTCL', 'BTN Subsidy', 'BTN Existing','BTN Syariah']

    
            for sheet in sheet_names:
                dfs = pd.read_excel(fs10_path, sheet_name=sheet, dtype=str, header=None, names=header)
                dfs = dfs.iloc[:, 0:1]
                dfs.drop_duplicates(inplace=True)
                dfs.reset_index(drop=True, inplace=True)
                fs10s.append(dfs)

            # Concatenate all dataframes
            fs10 = pd.concat(fs10s, ignore_index=True)

            return fs10
        else:
            return

    def run_checks(self):
        print("Starting data quality checks...")
        df02, df02copy = self.load_fs02_files()
        fs10 = self.load_fs10_files()
        # To store results for the Excel report
        results_all_check = []
        errors_all = []
        
            # Initialize a dictionary to store errors
        all_errors = {}        
        
        if self.proposal_error_var.get():
            all_errors['Proposal Error'] = []
        if self.missing_policy_var.get():
            all_errors['Missing Policy'] = []
        if self.blank_policy_number_var.get():
            all_errors['Blank Policy Number'] = []
        if self.blank_account_code_event_code_var.get():
            all_errors['Blank Account & Event Code'] = []
        if self.missing_account_map_var.get():
            all_errors['Missing Account MAP'] = []
        if self.missing_fs10_var.get():
            all_errors['Missing FS10'] = []
        if self.list_acf_credit_life_policy_var.get():
            all_errors['List ACF Credit Life Policy'] = []
        if self.non_idr_var.get():
            all_errors['List Non IDR OC=FC'] = []       
        
        fs06_files = sorted([f for f in os.listdir(self.fs06path) if f.endswith('.csv')])
        first_filepath = os.path.join(self.fs06path, fs06_files[0])
        first_df = pd.read_csv(first_filepath, encoding= 'utf-8-sig', dtype = str, keep_default_na=False, na_values=[''], low_memory=False)
        column_names = first_df.columns.tolist()
        
        # 2. Loop through FS06 files and run the checks
        for filename in fs06_files:
            print(f"Checking file: {filename}...")
            filepath = os.path.join(self.fs06path, filename)
            df = pd.read_csv(filepath, encoding= 'utf-8-sig', dtype = str, keep_default_na=False, na_values=[''], low_memory=False)
            df.columns = column_names

            # Initialize error counts and results for this file
            date_errors = 0
            proposal_error_count = 0
            missing_count = 0
            blanks_count = 0
            blank_code_count = 0
            missing_key_count = 0
            missing_fs0610_count = 0
            non_idr_count = 0            

#             event_date_errors = self.event_date_check(df, filename.split('_')[4])
#             cash_flow_errors = self.cash_flow_date_check(df, filename.split('_')[4])
            

            if self.date_error_var.get():
                date_errors = self.date_check(df, filename.split('_')[4])
                print(date_errors)

            if self.proposal_error_var.get():
                proposal_error_count, proposal_errors = self.proposal_check(df, df02, filename)
                if not proposal_errors.empty:
                    all_errors['Proposal Error'].append(proposal_errors)
            
            if self.missing_policy_var.get():
                missing_count, missing_policy_errors = self.missing_policy_check(df, df02, filename)
                if not missing_policy_errors.empty:
                    all_errors['Missing Policy'].append(missing_policy_errors)

            if self.list_acf_credit_life_policy_var.get():
                clp = self.credit_life_policy(df, filename)
                if not clp.empty:
                    all_errors['List ACF Credit Life Policy'].append(clp)

            df = self.merge_with_dpl(df)    

            if self.blank_policy_number_var.get():
                blanks_count, merged_data = self.blanks_check(df, filename)
                if not merged_data.empty:
                    all_errors['Blank Policy Number'].append(merged_data)

            if self.blank_account_code_event_code_var.get():
                blank_code_count, df_filtered = self.blank_code_check(df, filename)
                if not df_filtered.empty:
                    all_errors['Blank Account & Event Code'].append(df_filtered)

            if self.missing_account_map_var.get():
                missing_key, missing_key_count = self.dpl_key_check(df, filename)
                if not missing_key.empty:
                    all_errors['Missing Account MAP'].append(missing_key)
                    
            if self.missing_fs10_var.get():
                missing_fs0610, missing_fs0610_count = self.fs0610_check(df, fs10, df02copy, filename)
                if not missing_fs0610.empty:
                    all_errors['Missing FS10'].append(missing_fs0610)

            if self.non_idr_var.get():
                non_idr, non_idr_count = self.non_idr_list(df, filename)
                if not non_idr.empty:
                    all_errors['List Non IDR OC=FC'].append(non_idr)
            

            # Decrease the error count for 'NA' values in 'Cash Flow Type' column
#             na_count = len(proposal_errors[proposal_errors['Cash Flow Type'] == 'NA'])
#             proposal_error_count -= na_count
        
            # Remove rows with 'NA' values in 'Cash Flow Type' from proposal_errors DataFrame
#             proposal_errors = proposal_errors[proposal_errors['Cash Flow Type'] != 'NA']

            # Append the error rows to the respective lists in the dictionary


            # Storing results
            total_errors = date_errors + proposal_error_count + missing_count + blanks_count + blank_code_count + missing_key_count + missing_fs0610_count + non_idr_count

            status = "Passed" if total_errors == 0 else "Failed"
            results_all_check.append([filename, status])

            if status == "Failed":
                error_details_list = []
                if self.date_error_var.get():
                    error_details_list.append(f"Date Errors: {date_errors}")
                if self.proposal_error_var.get():
                    error_details_list.append(f"Proposal Error: {proposal_error_count}")
                if self.missing_policy_var.get():
                    error_details_list.append(f"Missing Policy: {missing_count}")
                if self.blank_policy_number_var.get():
                    error_details_list.append(f"Blank Policy Number: {blanks_count}")
                if self.blank_account_code_event_code_var.get():
                    error_details_list.append(f"Blank Account & Event Code: {blank_code_count}")
                if self.missing_account_map_var.get():
                    error_details_list.append(f"Missing Account MAP: {missing_key_count}")
                if self.missing_fs10_var.get():
                    error_details_list.append(f"Missing FS10: {missing_fs0610_count}")
                if self.non_idr_var.get():
                    error_details_list.append(f"List Non IDR OC=FC: {non_idr_count}")

                error_details = "\n".join(error_details_list)
                errors_all.append([filename, status, error_details])

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        last_part = os.path.basename(self.fs06path)
        new_name = f"DQ_Report_{timestamp}_{last_part}.xlsx"

        output_path = self.selected_output_path
        report_path = os.path.join(output_path, new_name)                
                
        writer = pd.ExcelWriter(report_path, engine='xlsxwriter')
        for sheet_name, data_frames in all_errors.items():
            if data_frames:
                df_combined = pd.concat(data_frames, ignore_index=True)
                df_combined.to_excel(writer, sheet_name=sheet_name, index=False)

        # 3. Generate the Excel report
        print("Generating Excel report...")
        

        # Write All Data Quality Check sheet
        df_results = pd.DataFrame(results_all_check, columns=["File", "Status"])
        df_results.index += 1
        df_results.to_excel(writer, sheet_name='All Data Quality Check', index_label="No")

        # Write Errors sheet
        df_errors = pd.DataFrame(errors_all, columns=["File", "Status", "Error Data"])
        df_errors.index += 1
        df_errors.to_excel(writer, sheet_name='Errors', index_label="No")
        
        print("All checks complete!")

        writer.close()

        print(f"Report generated: {new_name}")


if __name__ == '__main__':
    app = DataQualityChecker(None)
    app.title("FS06 DATA QUALITY CHECKER")
    # GUI headers and other labels/buttons here
    app.mainloop()
