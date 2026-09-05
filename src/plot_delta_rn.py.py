import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Define paths smartly based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

input_excel = os.path.join(PROJECT_ROOT, 'results', 'all_delta_rn_data.xlsx')
output_dir = os.path.join(PROJECT_ROOT, 'figures', 'delta_rn_plots')

# Ensure figures directory exists
os.makedirs(output_dir, exist_ok=True)

# Check if the Excel file exists before trying to read it
if not os.path.exists(input_excel):
    print(f"❌ Error: The file was not found at '{input_excel}'")
    print("Please make sure you have run the 'extract_delta_rn_all.py' script successfully first.")
    exit()

# 2. Read the Excel file
print("Reading Excel file...")
xls = pd.ExcelFile(input_excel)

# 3. Loop through each sheet and plot
for sheet_name in xls.sheet_names:
    print(f"Plotting Delta Rn for sheet '{sheet_name}'...")
    df = pd.read_excel(xls, sheet_name=sheet_name)
    
    # Check if 'Cycle' column exists
    if 'Cycle' not in df.columns:
        print(f"  ⚠️ Skipping sheet '{sheet_name}' (No 'Cycle' column found).")
        continue
        
    # Create a new figure for this sheet
    plt.figure(figsize=(12, 8))
    
    # Plot each sample column (skip 'Cycle' column)
    for col in df.columns:
        if col != 'Cycle':
            # Plot Cycle vs Delta Rn
            plt.plot(df['Cycle'], df[col], label=col, linewidth=1.5, alpha=0.8)
            
    # Chart formatting
    plt.title(f'Delta Rn Amplification Curves - File {sheet_name}', fontsize=16, fontweight='bold')
    plt.xlabel('Cycle Number', fontsize=12)
    plt.ylabel('Delta Rn (dRn)', fontsize=12)
    plt.axhline(0, color='black', linewidth=0.8, linestyle='-') # Add a zero line for better visualization
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Place legend outside the plot
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0., fontsize=8)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(output_dir, f"delta_rn_file_{sheet_name}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close() # Close the figure to free up memory
    
    print(f"  ✅ Saved to '{output_path}'")

print("\n🎉 All Delta Rn plots generated successfully!")