import pandas as pd
from pathlib import Path

def normalize_excel_data(input_filename, output_filename):
    """
    این تابع فایل اکسل را می‌خواند، تمام شیت‌ها را بین 0 تا 100 نرمال می‌کند 
    و خروجی را در پوشه results ذخیره می‌کند.
    """
    print("شروع پردازش فایل...")
    
    # پیدا کردن مسیر ریشه پروژه (با فرض اینکه این اسکریپت در پوشه src قرار دارد)
    root_dir = Path(__file__).parent.parent
    input_path = root_dir / 'results' / input_filename
    output_path = root_dir / 'results' / output_filename
    
    # بررسی وجود فایل
    if not input_path.exists():
        print(f"خطا: فایل '{input_path}' پیدا نشد! لطفاً مطمئن شوید فایل در پوشه results قرار دارد.")
        return

    # خواندن فایل اکسل با تمام شیت‌های آن
    xls = pd.ExcelFile(input_path)
    
    print("در حال نرمال‌سازی داده‌ها بین 0 تا 100...")
    # ایجاد یک فایل اکسل جدید برای نوشتن خروجی
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name in xls.sheet_names:
            # خواندن شیت فعلی
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # ستون‌هایی که نباید نرمال شوند (مثل شمارهCycle یا ستون‌های بدون نام/ایندکس)
            # در داده‌های شما ستون Cycle نباید نرمال شود
            cols_to_skip = ['Cycle', 'HEAD', 'Unnamed: 0', 'Unnamed: 1']
            cols_to_normalize = [col for col in df.columns if col not in cols_to_skip]
            
            for col in cols_to_normalize:
                # بررسی اینکه آیا ستون عددی است یا خیر (ستون‌های متنی نرمال نمی‌شوند)
                if pd.api.types.is_numeric_dtype(df[col]):
                    min_val = df[col].min()
                    max_val = df[col].max()
                    
                    if pd.isna(min_val) or pd.isna(max_val):
                        continue
                    if max_val != min_val:
                        df[col] = (df[col] - min_val) / (max_val - min_val) * 100
                    else:
                        df[col] = 0.0 # اگر تمام داده‌های یک ستون برابر باشند
            
            # ذخیره شیت نرمال شده در فایل جدید
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
    print(f"فایل اکسل نرمال‌شده با موفقیت ساخته شد:\n{output_path}")

if __name__ == "__main__":
    # نام فایل اکسل خام خود را اینجا بنویسید (فایلی که در پوشه results است)
    # طبق پیام اول شما، نام فایل all_delta_rn_data.xlsx فرض شده است
    INPUT_FILE = "all_delta_rn_data.xlsx"  
    
    # نام فایل خروجی نرمال شده
    OUTPUT_FILE = "normalized_all_delta_rn_data.xlsx"
    
    normalize_excel_data(INPUT_FILE, OUTPUT_FILE)