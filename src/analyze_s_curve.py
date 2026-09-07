import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ==========================================
# بخش تنظیمات (لطفا این اعداد را برای بهینه‌سازی تغییر دهید)
# ==========================================
CONFIG = {
    # حداقل فاصله بین خط پایه و بیشترین مقدار نمودار تا تکثیر محسوب شود
    'MIN_AMPLITUDE': 1000,  
    
    # تعداد سیکل‌های اول برای محاسبه خط پایه
    'BASELINE_CYCLES': 5,   
    
    # تعداد سیکل‌های آخر برای بررسی سکوشن (Plateau)
    'PLATEAU_CYCLES': 5,    
    
    # انحراف معیار مجاز برای خط پایه و سکوشن (درصدی از دامنه کل)
    # اگر این عدد 0.1 باشد، یعنی نوسانات ابتدا و انتها نباید بیشتر از 10% کل دامنه باشد
    'FLATNESS_THRESHOLD': 0.15, 
    
    # درصدی از دامنه که خط آستانه (Threshold) برای Ct در آن رسم می‌شود (20% = 0.2)
    'CT_THRESHOLD_PERCENT': 0.2, 
    
    # حداقل سیکلی که Ct باید در آن رخ دهد (سیکل‌های خیلی زودگذر نویز محسوب می‌شوند)
    'MIN_VALID_CT_CYCLE': 3     
}
# ==========================================

def check_s_shape(values, config):
    """
    بررسی می‌کند آیا نمودار شکل S دارد یا خیر.
    شرط 1: دامنه افزایش کافی باشد.
    شرط 2: ابتدای نمودار صاف باشد (خط پایه).
    شرط 3: انتهای نمودار صاف شده باشد (سکوشن).
    """
    baseline_cycles = config['BASELINE_CYCLES']
    plateau_cycles = config['PLATEAU_CYCLES']
    
    # محاسبه خط پایه و سکوشن با میانگین
    baseline = np.median(values[:baseline_cycles])
    plateau = np.median(values[-plateau_cycles:])
    amplitude = plateau - baseline
    
    # شرط 1: آیا اصلا تکثیر رخ داده است؟
    if amplitude < config['MIN_AMPLITUDE']:
        return False, baseline, amplitude
        
    # شرط 2: آیا ابتدای نمودار صاف است؟ (نوسانات نباید بیشتر از درصد مجاز از کل دامنه باشد)
    baseline_std = np.std(values[:baseline_cycles])
    if baseline_std > config['FLATNESS_THRESHOLD'] * amplitude:
        return False, baseline, amplitude
        
    # شرط 3: آیا انتهای نمودار صاف است؟ (بررسی سکوشن)
    plateau_std = np.std(values[-plateau_cycles:])
    if plateau_std > config['FLATNESS_THRESHOLD'] * amplitude:
        return False, baseline, amplitude
        
    return True, baseline, amplitude

def analyze_s_curves(input_path, output_excel, figures_dir):
    print(f"در حال خواندن فایل: {input_path}")
    
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)
        
    xls = pd.ExcelFile(input_path)
    results = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        if 'Cycle' not in df.columns:
            continue
            
        plt.figure(figsize=(12, 8))
        
        for col in df.columns:
            if col in ['Cycle', 'HEAD']:
                continue
                
            cycles = df['Cycle'].values
            values = df[col].values
            
            # 1. بررسی شکل S
            is_positive, baseline, amplitude = check_s_shape(values, CONFIG)
            
            # 2. محاسبه Ct فقط برای نمونه‌های مثبت
            ct_value = np.nan
            threshold_level = np.nan
            
            if is_positive:
                # تنظیم خط آستانه (مثلا 20% بالاتر از خط پایه)
                threshold_level = baseline + (CONFIG['CT_THRESHOLD_PERCENT'] * amplitude)
                
                # پیدا کردن نقطه عبور از آستانه (Interpolation)
                for i in range(1, len(values)):
                    if cycles[i] <= CONFIG['MIN_VALID_CT_CYCLE']:
                        continue # نادیده گرفتن نویزهای ابتدایی
                        
                    if values[i-1] < threshold_level <= values[i]:
                        ct_value = cycles[i-1] + (threshold_level - values[i-1]) / (values[i] - values[i-1])
                        break
                        
            # 3. رسم نمودار
            if is_positive:
                label = f"{col} (Pos, Ct={ct_value:.2f})" if not np.isnan(ct_value) else f"{col} (Pos, No Ct)"
                plt.plot(cycles, values, label=label, linewidth=1.5, color='blue')
                # رسم خط آستانه برای نمونه‌های مثبت
                if not np.isnan(ct_value):
                    plt.axhline(y=threshold_level, color='black', linestyle='--', linewidth=0.5, alpha=0.5)
            else:
                plt.plot(cycles, values, label=f"{col} (Neg)", linewidth=1, color='gray', alpha=0.5)
                
            # ذخیره نتایج
            results.append({
                'Sheet': sheet_name,
                'Sample': col,
                'Status': 'Positive' if is_positive else 'Negative',
                'Ct_Value': round(ct_value, 2) if not np.isnan(ct_value) else None
            })
            
        # تنظیمات ظاهری نمودار
        plt.title(f'S-Curve Analysis - {sheet_name}', fontsize=14)
        plt.xlabel('Cycle', fontsize=12)
        plt.ylabel('Delta Rn (Raw)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
        plt.tight_layout()
        
        plot_path = os.path.join(figures_dir, f"{sheet_name}_scurve_analysis.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"نمودار ذخیره شد: {plot_path}")

    # ذخیره فایل اکسل نتایج
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_excel, index=False)
    print(f"\nگزارش تحلیل شکل S ذخیره شد:\n{output_excel}")

if __name__ == "__main__":
    results_dir = 'results'
    figures_dir = 'figures'
    
    input_filename = 'all_delta_rn_data.xlsx' 
    output_filename = 's_curve_ct_results.xlsx' 
    
    input_path = os.path.join(results_dir, input_filename)
    output_path = os.path.join(results_dir, output_filename)
    
    if os.path.exists(input_path):
        analyze_s_curves(input_path, output_path, figures_dir)
    else:
        print(f"خطا: فایل '{input_path}' پیدا نشد!")