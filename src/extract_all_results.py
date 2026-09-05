import pandas as pd
import os

def find_header_row(df_raw):
    """Helper function to find the row containing 'Well Position'"""
    for i in range(min(30, len(df_raw))):
        if df_raw.iloc[i].astype(str).str.contains('Well Position', case=False).any():
            return i
    return None

# 1. Define directories
data_dir = "../data"
output_file = "../results/all_files_extracted.xlsx"

# Get all .xls files in the data directory
try:
    files = [f for f in os.listdir(data_dir) if f.endswith('.xls')]
    if not files:
        print(f"No .xls files found in '{data_dir}'.")
        exit()
except FileNotFoundError:
    print(f"Error: The data directory '{data_dir}' was not found!")
    exit()

print(f"Found {len(files)} Excel files. Starting processing...\n")

# Ensure results directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# 2. Loop through each file and save to a separate sheet
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        print(f"Processing '{file_name}'...")
        
        try:
            # --- STEP A: Read Sample Setup to find wells with Sample Names ---
            df_setup_raw = pd.read_excel(file_path, sheet_name="Sample Setup", header=None)
            setup_header_row = find_header_row(df_setup_raw)
            
            if setup_header_row is None:
                print(f"  ⚠️ Warning: 'Well Position' not found in Sample Setup for '{file_name}'. Skipping.")
                continue
                
            df_setup = pd.read_excel(file_path, sheet_name="Sample Setup", skiprows=setup_header_row)
            df_setup.columns = df_setup.columns.str.strip()
            df_setup['Well Position'] = df_setup['Well Position'].astype(str).str.strip()
            
            # Filter rows where 'Sample Name' is not null (empty)
            df_setup_clean = df_setup.dropna(subset=['Sample Name'])
            
            # Create a dictionary {Well: SampleName} and a list of wells to extract
            well_to_sample = dict(zip(df_setup_clean['Well Position'], df_setup_clean['Sample Name']))
            wells_to_extract = list(well_to_sample.keys())
            
            if not wells_to_extract:
                print(f"  ⚠️ Warning: No samples with names found in '{file_name}'. Skipping.")
                continue

            # --- STEP B: Read Raw Data ---
            df_raw = pd.read_excel(file_path, sheet_name="Raw Data", header=None)
            raw_header_row = find_header_row(df_raw)
            
            if raw_header_row is None:
                print(f"  ⚠️ Warning: 'Well Position' not found in Raw Data for '{file_name}'. Skipping.")
                continue
                
            df = pd.read_excel(file_path, sheet_name="Raw Data", skiprows=raw_header_row)
            df.columns = df.columns.str.strip()
            df['Well Position'] = df['Well Position'].astype(str).str.strip()
            df['Cycle'] = pd.to_numeric(df['Cycle'], errors='coerce')
            
            # Find the x1-m1 column safely
            x_col = [c for c in df.columns if 'x1' in c.lower() and 'm1' in c.lower()][0]

            # --- STEP C: Build the Final Table ---
            df_filtered = df[df['Well Position'].isin(wells_to_extract)].copy()
            all_cycles = sorted(df['Cycle'].dropna().unique())
            result_df = pd.DataFrame({'Cycle': all_cycles})

            for well in wells_to_extract:
                well_data = df_filtered[df_filtered['Well Position'] == well]
                cycle_to_val = dict(zip(well_data['Cycle'], well_data[x_col]))
                
                sample_name = well_to_sample.get(well, well)
                # Use a unique column name to avoid duplicates (e.g. "Ef1a-old-63 (C3)")
                col_name = f"{sample_name} ({well})"
                
                result_df[col_name] = result_df['Cycle'].map(cycle_to_val)

            # --- STEP D: Save to a separate sheet ---
            # Sheet names cannot contain certain characters and must be <= 31 chars
            sheet_name = os.path.splitext(file_name)[0] # e.g., "1", "2"
            result_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"  ✅ Successfully added as sheet '{sheet_name}' with {len(wells_to_extract)} samples")
            
        except Exception as e:
            print(f"  ❌ Error processing '{file_name}': {e}")

print(f"\n🎉 All processing finished! Master file saved to: '{output_file}'")