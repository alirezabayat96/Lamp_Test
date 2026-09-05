import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Define paths
input_excel = "./results/all_files_extracted.xlsx"
output_dir = "./figures"

# Ensure figures directory exists
os.makedirs(output_dir, exist_ok=True)

# 2. Read the Excel file
print("Reading Excel file...")
xls = pd.ExcelFile(input_excel)

# 3. Loop through each sheet and plot
for sheet_name in xls.sheet_names:
    print(f"Plotting sheet '{sheet_name}'...")
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
            # Plot Cycle vs Fluorescence (x1-m1)
            plt.plot(df['Cycle'], df[col], label=col, linewidth=1.5, alpha=0.8)
            
    # Chart formatting
    plt.title(f'Amplification Curves - File {sheet_name}', fontsize=16, fontweight='bold')
    plt.xlabel('Cycle Number', fontsize=12)
    plt.ylabel('Fluorescence (x1-m1)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Place legend outside the plot
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0., fontsize=8)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(output_dir, f"amplification_file_{sheet_name}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close() # Close the figure to free up memory
    
    print(f"  ✅ Saved to '{output_path}'")

print("\n🎉 All plots generated successfully!")