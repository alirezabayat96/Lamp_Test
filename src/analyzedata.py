import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_and_plot(input_path, output_excel, figures_dir):
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
            
            # 1. محاسبه خط پایه (میانگین 5 سیکل اول)
            baseline = np.mean(values[:5])
            max_val = np.max(values)
            amplitude = max_val - baseline
            
            # 2. تشخیص مثبت یا منفی بودن
            # اگر دامنه افزایش بیشتر از 1000 باشد، نمونه مثبت است (این عدد را می‌توانید تغییر دهید)
            is_positive = amplitude > 30000
            
            # 3. محاسبه Ct
            ct_value = np.nan
            threshold_level = np.nan
            
            if is_positive:
                # تنظیم خط آستانه در 20% بالاتر از خط پایه
                threshold_level = baseline + (0.2 * amplitude)
                
                # پیدا کردن سیکلی که نمودار از آستانه عبور می‌کند
                for i in range(1, len(values)):
                    if values[i-1] < threshold_level <= values[i]:
                        # محاسبه دقیق Ct با استفاده از فرمول interpolation خطی
                        ct_value = cycles[i-1] + (threshold_level - values[i-1]) / (values[i] - values[i-1])
                        break
                        
                # رسم نمودار برای نمونه مثبت (سبز)
                plt.plot(cycles, values, label=f"{col} (Pos, Ct={ct_value:.2f})", linewidth=1.5, color='green')
                # رسم خط آستانه
                plt.axhline(y=threshold_level, color='gray', linestyle='--', linewidth=0.5)
            else:
                # رسم نمودار برای نمونه منفی (قرمز)
                plt.plot(cycles, values, label=f"{col} (Neg)", linewidth=1.5, color='red', alpha=0.6)
                
            # ذخیره نتایج برای فایل اکسل
            results.append({
                'Sheet': sheet_name,
                'Sample': col,
                'Status': 'Positive' if is_positive else 'Negative',
                'Ct_Value': round(ct_value, 2) if not np.isnan(ct_value) else None,
                'Baseline': round(baseline, 2),
                'Max_Delta_Rn': round(max_val, 2)
            })
            
        # تنظیمات نمودار شیت
        plt.title(f'Raw Amplification Curves - {sheet_name}', fontsize=14)
        plt.xlabel('Cycle', fontsize=12)
        plt.ylabel('Delta Rn', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=7)
        plt.tight_layout()
        
        # ذخیره نمودار
        plot_path = os.path.join(figures_dir, f"{sheet_name}_raw_analysis.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"نمودار ذخیره شد: {plot_path}")

    # 4. ذخیره گزارش در فایل اکسل
    results_df = pd.DataFrame(results)
    results_df.to_excel(output_excel, index=False)
    print(f"\nگزارش Ct و وضعیت نمونه‌ها ذخیره شد:\n{output_excel}")

if __name__ == "__main__":
    results_dir = 'results'
    figures_dir = 'figures'
    
    input_filename = 'all_delta_rn_data.xlsx' # فایل داده‌های خام
    output_filename = 'ct_analysis_results.xlsx' # فایل گزارش Ct
    
    input_path = os.path.join(results_dir, input_filename)
    output_path = os.path.join(results_dir, output_filename)
    
    if os.path.exists(input_path):
        analyze_and_plot(input_path, output_path, figures_dir)
    else:
        print(f"خطا: فایل '{input_path}' پیدا نشد!")