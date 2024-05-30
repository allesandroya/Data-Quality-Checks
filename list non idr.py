
import pandas as pd
import os

path = r'D:\Work Documents\Apps\OFCGL Jan Feb'

dfs = []
all_files = sorted([f for f in os.listdir(path) if f.endswith('.csv')])

# Load the header from the first file
header_file_path = os.path.join(path, all_files[0])
first_file_df = pd.read_csv(header_file_path, encoding='utf-8-sig', dtype= str, keep_default_na=False, na_values=[''], low_memory=False)
header = first_file_df.columns.tolist()

for file in all_files:
    print(f"combining {file}...")
    file_path = os.path.join(path, file)
    
    df = pd.read_csv(file_path, encoding='utf-8-sig', dtype=str, keep_default_na=False, na_values=[''], low_memory=False)
    df.columns = header
    df_filtered = df[~df[df.columns[6]].isin(['IDR'])]
    df_filtered = df_filtered[df_filtered.iloc[:, 5] == df_filtered.iloc[:, 7]]


    dfs.append(df_filtered)

combined_df = pd.concat(dfs, ignore_index=True)   
indices_to_drop = [0,2,4,8,13]
indices_to_drop.extend(range(14, len(combined_df.columns)))
combined_df.drop(combined_df.columns[indices_to_drop], axis=1, inplace=True)
print(combined_df)