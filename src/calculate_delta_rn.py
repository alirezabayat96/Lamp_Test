import pandas as pd
import os

def find_header_row(df_raw):
    """Helper function to find the row containing 'Well Position'"""
    for i in range(min(30, len(df_raw))):
        if df_raw.iloc[i].astype(str).str.contains('Well Position', case=False).any():
            return i
    return None

# 1. Define paths smartly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'results', 'all_delta_rn_data.xlsx')

# Ensure results directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Get all .xls files
try:
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.xls')], key=lambda x: int(x.split('.')[0]))
except ValueError:
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.xls')])

if not files:
    print(f"No .xls files found in '{DATA_DIR}'")
    exit()

print(f"Found {len(files)} Excel files. Starting extraction of Delta Rn values...\n")

# 2. Loop through each file and save to a separate sheet
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    
    for file_name in files:
        file_path = os.path.join(DATA_DIR, file_name)
        print(f"Processing '{file_name}'...")
        
        try:
            # --- STEP A: Read Sample Setup to get Sample Names ---
            df_setup_raw = pd.read_excel(file_path, sheet_name="Sample Setup", header=None)
            setup_header = find_header_row(df_setup_raw)
            
            if setup_header is None:
                print(f"  ⚠️ Warning: 'Well Position' not found in Sample Setup for '{file_name}'. Skipping.")
                continue
                
            df_setup = pd.read_excel(file_path, sheet_name="Sample Setup", skiprows=setup_header)
            df_setup.columns = df_setup.columns.str.strip()
            df_setup['Well Position'] = df_setup['Well Position'].astype(str).str.strip()
            
            # Keep only rows with Sample Name
            df_setup_clean = df_setup.dropna(subset=['Sample Name'])
            
            # Create dictionary {Well Position: Sample Name}
            well_to_sample = dict(zip(df_setup_clean['Well Position'], df_setup_clean['Sample Name']))
            wells_to_extract = list(well_to_sample.keys())
            
            if not wells_to_extract:
                print(f"  ⚠️ Warning: No samples with names found in '{file_name}'. Skipping.")
                continue

            # --- STEP B: Read Amplification Data to get Delta Rn ---
            df_amp_raw = pd.read_excel(file_path, sheet_name="Amplification Data", header=None)
            amp_header = find_header_row(df_amp_raw)
            
            if amp_header is None:
                print(f"  ⚠️ Warning: 'Well Position' not found in Amplification Data for '{file_name}'. Skipping.")
                continue
                
            df_amp = pd.read_excel(file_path, sheet_name="Amplification Data", skiprows=amp_header)
            df_amp.columns = df_amp.columns.str.strip()
            df_amp['Well Position'] = df_amp['Well Position'].astype(str).str.strip()
            df_amp['Cycle'] = pd.to_numeric(df_amp['Cycle'], errors='coerce')
            
            # CRITICAL CHANGE: Check if 'Delta Rn' exists and convert to numeric
            if 'Delta Rn' not in df_amp.columns:
                print(f"  ⚠️ Warning: 'Delta Rn' column not found in '{file_name}'. Skipping.")
                continue
                
            df_amp['Delta Rn'] = pd.to_numeric(df_amp['Delta Rn'], errors='coerce')

            # --- STEP C: Build the Final Table (Cycle vs Sample Delta Rn) ---
            df_filtered = df_amp[df_amp['Well Position'].isin(wells_to_extract)].copy()
            df_filtered = df_filtered.dropna(subset=['Delta Rn', 'Cycle'])
            
            all_cycles = sorted(df_amp['Cycle'].dropna().unique())
            result_df = pd.DataFrame({'Cycle': all_cycles})

            for well in wells_to_extract:
                well_data = df_filtered[df_filtered['Well Position'] == well]
                cycle_to_delta_rn = dict(zip(well_data['Cycle'], well_data['Delta Rn']))
                
                sample_name = well_to_sample.get(well, well)
                # Create a unique column name like "Ef1a-old-PTC (B5)"
                col_name = f"{sample_name} ({well})"
                
                result_df[col_name] = result_df['Cycle'].map(cycle_to_delta_rn)

            # --- STEP D: Save to a separate sheet ---
            # Sheet names cannot contain certain characters and must be <= 31 chars
            sheet_name = os.path.splitext(file_name)[0] # e.g., "1", "2"
            result_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"  ✅ Successfully added sheet '{sheet_name}' with {len(wells_to_extract)} samples")
            
        except Exception as e:
            print(f"  ❌ Error processing '{file_name}': {e}")

print(f"\n🎉 All processing finished! Master file saved to: '{OUTPUT_FILE}'")