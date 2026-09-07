import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_normalized_data(input_path, output_dir):
    print(f"در حال خواندن فایل برای رسم نمودار: {input_path}")
    
    # ایجاد پوشه figures در صورت عدم وجود
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # خواندن فایل اکسل نرمال شده
    xls = pd.ExcelFile(input_path)
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # بررسی وجود ستون Cycle
        if 'Cycle' not in df.columns:
            print(f"شیت '{sheet_name}' ستون 'Cycle' ندارد، رد شدن...")
            continue
            
        plt.figure(figsize=(12, 8))
        
        # رسم نمودار برای هر ستون (به جز ستون‌های شناسایی)
        for col in df.columns:
            if col not in ['Cycle', 'HEAD']:
                plt.plot(df['Cycle'], df[col], label=col, linewidth=1.5)
        
        # تنظیمات نمودار
        plt.title(f'Amplification Curves - {sheet_name}', fontsize=14)
        plt.xlabel('Cycle', fontsize=12)
        plt.ylabel('Normalized Delta RN (0-100)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # قرار دادن راهنما (Legend) بیرون از نمودار برای جلوگیری از شلوغی
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., fontsize=8)
        
        # تنظیم فاصله حاشیه‌ها
        plt.tight_layout()
        
        # ذخیره نمودار با کیفیت بالا در پوشه figures
        plot_filename = f"{sheet_name}_normalized_plot.png"
        plot_path = os.path.join(output_dir, plot_filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close() # بستن نمودار برای آزادسازی حافظه
        
        print(f"نمودار ذخیره شد: {plot_path}")

if __name__ == "__main__":
    results_dir = 'results'
    figures_dir = 'figures'
    
    input_filename = 'normalized_all_delta_rn_data.xlsx' # نام فایل نرمال شده
    input_path = os.path.join(results_dir, input_filename)
    
    if os.path.exists(input_path):
        plot_normalized_data(input_path, figures_dir)
    else:
        print(f"خطا: فایل '{input_path}' پیدا نشد!")
        print("لطفاً ابتدا اسکریپت نرمال‌سازی (normalize_data.py) را اجرا کنید.")