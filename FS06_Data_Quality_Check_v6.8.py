import tkinter as tk
from tkinter import filedialog, Label, Button
import os
import pandas as pd
import numpy as np
import time

class DataQualityChecker(tk.Tk):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initialize()
        self.grouped_df = None

    def initialize(self):
        self.grid()

#         tk.Label(self, text="Please specify your FS02 and FS06 input folders:", font="Calibri 12").grid(row=0, column=0, sticky='w')

#         tk.Button(self, text="Search FS02 Folder", command=lambda: self.inputfunc('FS02'), fg="white", bg="red").grid(row=1, column=0, sticky='w')
#         self.fs02_label = tk.Label(self, font="Calibri 12")
#         self.fs02_label.grid(row=1, column=1, sticky='w')

#         tk.Button(self, text="Search FS06 Folder", command=lambda: self.inputfunc('FS06'), fg="white", bg="red").grid(row=2, column=0, sticky='w')
#         self.fs06_label = tk.Label(self, font="Calibri 12")
#         self.fs06_label.grid(row=2, column=1, sticky='w')

#         tk.Button(self, text="Select Output Directory", command=self.output_directory, fg="white", bg="blue").grid(row=3, column=0, sticky='w')
#         self.output_label = tk.Label(self, font="Calibri 12")
#         self.output_label.grid(row=3, column=1, sticky='w')

#         tk.Button(self, text="Start Data Quality Check", command=self.run_checks, fg="white", bg="green").grid(row=4, column=0, sticky='w')

        # Styles and Utilities
        self.bg_color = "#282c34"  # Dark background color
        self.text_color = "#a9b7c6"  # Light text color
        self.highlight_color = "dark orange"
        self.configure(bg=self.bg_color)
        self.create_gui_elements()

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
        self.create_label("\nScript/Python will be used for data quality, focussing in checking:", 12).grid(row=2, column=0, sticky='w')
        self.create_label("1). Anomali Event Date & Cash Flow Date", 12).grid(row=3, column=0, sticky='w')
        self.create_label("2). Blank Policy Number, Event & Account Code", 12).grid(row=4, column=0, sticky='w')
        self.create_label("3). Proposal Status", 12).grid(row=5, column=0, sticky='w')
        self.create_label("4). Missing Policy", 12).grid(row=6, column=0, sticky='w')

        self.create_label("\nPlease pay attention to the following points before inputting your data:", 12).grid(row=7, column=0, sticky='w')
        self.create_label("1). Make sure that the data you input has 32 columns.", 12).grid(row=8, column=0, sticky='w')
        self.create_label("2). Make sure all the latest FS02 files has been placed in folder FS02", 12).grid(row=9, column=0, sticky='w')
        self.create_label("3). Output directory must be different from both FS02 or FS06 folder path.", 12).grid(row=11, column=0, sticky='w')
        self.create_label("4). Only CSV files are allowed in the FS06 folder.\n", 12).grid(row=12, column=0, sticky='w')
        
    def create_label(self, text, font_size, color=None, bold=False):
        color = color or self.text_color
        font_style = "bold" if bold else "normal"
        label = Label(self, text=text, font=("Calibri", font_size, font_style), fg=color, bg=self.bg_color)
        return label

    
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

        # Concatenate the columns in both DataFrames to form the composite keys
        df['composite_key'] = df[df.columns[10]].astype(str) + df[df.columns[9]].astype(str)
        dpl['composite_key'] = dpl['LK_MATCH_KEY4'].astype(str) + dpl['LK_MATCH_KEY2'].astype(str)

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
        df['Cash Flow Date1'] = pd.to_datetime(df.iloc[:, 12], format='%Y/%m/%d', errors='coerce')
        df['Event Date1'] = pd.to_datetime(df.iloc[:, 11], format='%Y/%m/%d', errors='coerce')            

        # Extract the day, month, and year
        df['day'] = df['Cash Flow Date1'].dt.day
        df['month'] = df['Cash Flow Date1'].dt.month
        df['year'] = df['Cash Flow Date1'].dt.year

        df['day2'] = df['Event Date1'].dt.day
        df['month2'] = df['Event Date1'].dt.month
        df['year2'] = df['Event Date1'].dt.year

        year, month, day = int(date_from_filename[:4]), int(date_from_filename[4:6]), int(date_from_filename[6:])

        cf_below_year = df['year'] < year
        ed_below_year = df['year2'] < year
        cf_above_filename = (df['year'] > year) | ((df['year'] == year) & ((df['month'] > month) | ((df['month'] == month) & (df['day'] > day))))
        ed_above_filename = (df['year2'] > year) | ((df['year2'] == year) & ((df['month2'] > month) | ((df['month2'] == month) & (df['day2'] > day))))
        
        both_below_year = cf_below_year & ed_below_year
        both_above_filename = cf_above_filename & ed_above_filename        
        mask3 = cf_below_year & (df['year2'] == year)
        
        countFalse = both_below_year.sum() + both_above_filename.sum() + mask3.sum()
        return countFalse
    
    def blanks_check(self, df, filename):
        if not hasattr(self, 'directory_path') or not self.directory_path:
            print("Please select the DPL_LOOKUP file first.")
            return df
        
        print("Running blanks Policy Number check...")
        
        coapath = os.path.join(self.directory_path, 'List ACF CoA for DQ Blank Policy.xlsx')
        coa = pd.read_excel(coapath , sheet_name='New CoA')
          
        merged_data = pd.DataFrame()
        grouped_df2 = self.grouped_df
        
        grouped_df2[grouped_df2.columns[0]] = grouped_df2[grouped_df2.columns[0]].astype(str)
        
        # Filter rows where the column at index 1 (i.e., 'Policy Number') is either NaN or blank
        df_filtered = grouped_df2[(grouped_df2.iloc[:, 0].isna()) | (grouped_df2.iloc[:, 0] == 'NULL')]


        if not df_filtered.empty:

            merged_data = pd.merge(df_filtered, coa['Account Code'], left_on=df_filtered.columns[6], right_on='Account Code', how = 'inner')
#             merged_data.drop(merged_data.columns[13:41], axis=1, inplace=True)
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
            # List of column indices to drop
        indices_to_drop = [0, 2, 4, 8, 13]

        # Adding indices of columns after index 13
        indices_to_drop.extend(range(14, len(new_df2.columns)))

        # Drop columns by indices

        
        new_df2.drop(new_df2.columns[indices_to_drop], axis=1, inplace=True)
        
        key_col_df = new_df2.columns[0]
        key_col_df02 = df02.columns[0]

        if not key_col_df02.endswith('for check'):
            df02.rename(columns={key_col_df02: key_col_df02 + ' for check'}, inplace=True)
            key_col_df02 = key_col_df02 + ' for check'

        new_df2[key_col_df] = new_df2[key_col_df].astype(str)
        df02[key_col_df02] = df02[key_col_df02].astype(str)

        # Merge the dataframes
        merged_df = pd.merge(new_df2, df02[[key_col_df02]], left_on=key_col_df, right_on=key_col_df02, how='left')

        # Assuming 'filename' is defined elsewhere in your code or you can assign it a specific value
        # e.g., filename = "some_value.csv"

        # Extracting rows where the key from df02 is missing in the merged dataframe
        missing_policies = merged_df[merged_df[key_col_df02].isnull()]
        missing_policies['File Name'] = filename

        # Drop duplicates based on the original column in df
        missing_policies = missing_policies.drop_duplicates(subset=key_col_df)
        missing_policies = missing_policies[~missing_policies[key_col_df].isin(['NULL', ''])]
        missing_policies.drop(missing_policies.columns[13:41], axis=1, inplace=True)
        
        missing_count = len(missing_policies)

        return missing_count, missing_policies
    
    def load_fs02_files(self):
        print("Loading FS02 files...")
        # Create an empty list to hold dataframes
        dfs = []
        all_files = sorted([f for f in os.listdir(self.fs02path) if f.endswith('.csv')])

        # Load the header from the first file
        header_file_path = os.path.join(self.fs02path, all_files[0])
        first_file_df = pd.read_csv(header_file_path, encoding='unicode_escape', dtype={0: str}, low_memory=False)
        header = first_file_df.columns.tolist()
        first_file_df['FS02 File Name'] = all_files[0]  # Add new column with file name
        dfs.append(first_file_df)

        # Iterate through the rest of the files in the FS02 directory using the header from the first file
        for filename in all_files[1:]:
            filepath = os.path.join(self.fs02path, filename)

            df = pd.read_csv(filepath, encoding='unicode_escape', dtype={0: str}, header=None, names=header)
            df['FS02 File Name'] = filename  # Add new column with file name
            dfs.append(df)

        # Concatenate all dataframes in the list into a single dataframe
        df02 = pd.concat(dfs, ignore_index=True)

        # Drop duplicates keeping the last entry and reset index
        # df02 = df02.drop_duplicates(subset=header[0], keep='last').reset_index(drop=True)
        print("FS02 files loaded successfully!")

        return df02

    def run_checks(self):
        print("Starting data quality checks...")
        df02 = self.load_fs02_files()

        # To store results for the Excel report
        results_all_check = []
        errors_all = []

        output_path = self.selected_output_path
        report_path = os.path.join(output_path, 'DataQualityCheck_Report.xlsx')
        
            # Initialize a dictionary to store errors
        all_errors = {
            'Proposal Error': [],
            'Missing Policy': [],
            'Blank Policy Number': [],
            'Blank Account & Event Code': []
        }
        
        # 2. Loop through FS06 files and run the checks
        for filename in os.listdir(self.fs06path):
            print(f"Checking file: {filename}...")
            filepath = os.path.join(self.fs06path, filename)
            df = pd.read_csv(filepath, encoding= 'unicode_escape', dtype = {0:str}, keep_default_na=False, na_values=[''], low_memory=False)
            
#             event_date_errors = self.event_date_check(df, filename.split('_')[4])
#             cash_flow_errors = self.cash_flow_date_check(df, filename.split('_')[4])
            date_errors = self.date_check(df, filename.split('_')[4])
            proposal_error_count, proposal_errors = self.proposal_check(df, df02, filename)      

            
#             out_date_count, out_date_errors = self.out_date_check(df, df02, filename)
            missing_count, missing_policy_errors = self.missing_policy_check(df, df02, filename)
            df = self.merge_with_dpl(df)    
            blanks_count, merged_data = self.blanks_check(df, filename)
            blank_code_count, df_filtered = self.blank_code_check(df, filename)
          
            
            # Decrease the error count for 'NA' values in 'Cash Flow Type' column
#             na_count = len(proposal_errors[proposal_errors['Cash Flow Type'] == 'NA'])
#             proposal_error_count -= na_count
        
            # Remove rows with 'NA' values in 'Cash Flow Type' from proposal_errors DataFrame
#             proposal_errors = proposal_errors[proposal_errors['Cash Flow Type'] != 'NA']

            # Append the error rows to the respective lists in the dictionary
            if not proposal_errors.empty:
                all_errors['Proposal Error'].append(proposal_errors)
#             if not out_date_errors.empty:
#                 all_errors['Out Dated Check'].append(out_date_errors)
            if not missing_policy_errors.empty:
                all_errors['Missing Policy'].append(missing_policy_errors)
            
            if not merged_data.empty:
                all_errors['Blank Policy Number'].append(merged_data)
                
            if not df_filtered.empty:
                all_errors['Blank Account & Event Code'].append(df_filtered)


            # Storing results
            total_errors = date_errors + proposal_error_count + missing_count + blanks_count + blank_code_count

            status = "Passed" if total_errors == 0 else "Failed"
            results_all_check.append([filename, status])

            if status == "Failed":
                error_details = f"Date Errors: {date_errors}\nProposal Error: {proposal_error_count}\nMissing Policy: {missing_count}\nBlank Policy Number: {blanks_count}\nBlank Account & Event Code: {blank_code_count}"
                
                errors_all.append([filename, status, error_details])
                
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

        writer.save()
        print("Report generated: DataQualityCheck_Report.xlsx")


if __name__ == '__main__':
    app = DataQualityChecker(None)
    app.title("FS06 DATA QUALITY CHECKER")
    # GUI headers and other labels/buttons here
    app.mainloop()
