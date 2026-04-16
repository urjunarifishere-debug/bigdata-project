import sys
import os

# utils папкасын Python жолына қосу
sys.path.append(os.path.join(os.path.dirname(__file__), 'dataprocessor', 'utils'))

from data_cleaner import *  # dataprocessor/utils/data_cleaner.py импортталады

# Файлды автоматты түрде жүктеу функциясы
def load_file(file_path):
    """Файл типін автоматты түрде анықтап жүктейді"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    elif file_path.endswith('.txt'):
        return pd.read_csv(file_path, delimiter='\t')
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Қолдау көрсетілмейтін файл типі: {file_path}")

def analyze_file(file_path):
    """Бір файлды толық талдау және өзгерістерді көрсету"""
    
    print(f"\n{'='*80}")
    print(f"📁 ФАЙЛ: {file_path}")
    print('='*80)
    
    # 1. Файлды жүктеу
    df_original = load_file(file_path)
    print(f"\n✅ Файл сәтті жүктелді: {df_original.shape[0]} жол, {df_original.shape[1]} баған")
    
    # 2. Тазалау АЛДЫНДАҒЫ мәліметтер
    print("\n" + "─"*80)
    print("📊 ТАЗАЛАУ АЛДЫНДА (BEFORE CLEANING):")
    print("─"*80)
    
    # Null ақпарат
    null_info = get_null_info(df_original)
    if isinstance(null_info, pd.DataFrame) and not null_info.empty:
        print("\n🔍 Бос мәндер (Null values):")
        print(null_info.to_string(index=False))
    elif isinstance(null_info, pd.Series) and not null_info.empty:
        print("\n🔍 Бос мәндер (Null values):")
        print(null_info)
    else:
        print("\n✅ Бос мәндер жоқ")
    
    # Қайталанатын жолдар
    duplicates_before = df_original.duplicated().sum()
    if duplicates_before > 0:
        print(f"\n🔄 Қайталанатын жолдар: {duplicates_before} дана")
    else:
        print(f"\n✅ Қайталанатын жолдар жоқ")
    
    # 3. ТАЗАЛАУ
    print("\n" + "─"*80)
    print("🧹 ТАЗАЛАУ ПРОЦЕССІ (CLEANING PROCESS):")
    print("─"*80)
    
    result = clean_data(df_original.copy())
    
    # clean_data() нені қайтаратынын тексеру
    if isinstance(result, tuple):
        df_cleaned, detailed_changes = result
        report = analyze_changes(df_original, df_cleaned, detailed_changes)
    else:
        df_cleaned = result
        report = {
            'before_shape': df_original.shape,
            'after_shape': df_cleaned.shape,
            'duplicates_removed': duplicates_before - df_cleaned.duplicated().sum(),
            'rows_removed': df_original.shape[0] - df_cleaned.shape[0]
        }
    
    print("✅ 1. Барлық мәтіндік бағандардағы бос орындар кесілді")
    print("✅ 2. Қайталанатын жолдар жойылды")
    print("✅ 3. Бос мәндер толтырылды")
    
    # 4. Тазалау КЕЙІНГІ мәліметтер
    print("\n" + "─"*80)
    print("📊 ТАЗАЛАУ КЕЙІН (AFTER CLEANING):")
    print("─"*80)
    
    # Null ақпарат (тазалаудан кейін)
    null_info_after = get_null_info(df_cleaned)
    if isinstance(null_info_after, pd.DataFrame):
        if null_info_after.empty:
            print("\n✅ Барлық бос мәндер толтырылды!")
    elif isinstance(null_info_after, pd.Series):
        if null_info_after.sum() == 0:
            print("\n✅ Барлық бос мәндер толтырылды!")
    
    # Қайталанатын жолдар (тазалаудан кейін)
    duplicates_after = df_cleaned.duplicated().sum()
    if duplicates_after == 0:
        print(f"\n✅ Барлық қайталанатын жолдар жойылды!")
    
    # 5. ӨЗГЕРІСТЕР КЕСТЕСІ (DO & AFTER)
    print("\n" + "="*80)
    print("📊 ӨЗГЕРІСТЕР КЕСТЕСІ (CHANGES TABLE - DO & AFTER):")
    print("="*80)
    
    # Бос мәндер санын есептеу
    null_before = 0
    if isinstance(null_info, pd.DataFrame):
        null_before = null_info['Бос мәндер саны'].sum() if 'Бос мәндер саны' in null_info.columns else null_info.sum().sum()
    elif isinstance(null_info, pd.Series):
        null_before = null_info.sum()
    
    null_after = 0
    if isinstance(null_info_after, pd.DataFrame):
        null_after = null_info_after['Бос мәндер саны'].sum() if 'Бос мәндер саны' in null_info_after.columns else null_info_after.sum().sum()
    elif isinstance(null_info_after, pd.Series):
        null_after = null_info_after.sum()
    
    # Өзгерістер кестесі
    changes_data = {
        'Көрсеткіш': [
            'Жолдар саны',
            'Бағандар саны', 
            'Қайталанатын жолдар',
            'Бос мәндер (жалпы)',
            'Мәтіндік бағандардағы бос орындар'
        ],
        'Тазалау алдында (BEFORE)': [
            report['before_shape'][0],
            report['before_shape'][1],
            report['duplicates_removed'],
            null_before,
            'Бар'
        ],
        'Тазалау кейін (AFTER)': [
            report['after_shape'][0],
            report['after_shape'][1],
            0,
            null_after,
            'Жоқ (кесілді)'
        ],
        'Өзгеріс': [
            f"-{report['before_shape'][0] - report['after_shape'][0]}",
            '0',
            f"-{report['duplicates_removed']}",
            f"-{null_before - null_after}",
            'Толық кесілді'
        ]
    }
    
    changes_df = pd.DataFrame(changes_data)
    print(changes_df.to_string(index=False))
    
    return df_cleaned, report

# БАСТЫ ПРОГРАММА
if __name__ == "__main__":
    print("\n" + "🎯"*40)
    print("ДЕРЕКТЕРДІ ТАЗАЛАУ ТАПСЫРМАСЫ - ТОЛЫҚ ТАЛДАУ")
    print("🎯"*40)
    
    # Барлық файлдарды талдау
    files = ['../students.csv', '../employees.json', '../sales.txt', '../products.xlsx']
    
    all_results = {}
    for file in files:
        try:
            if os.path.exists(file):
                df_cleaned, report = analyze_file(file)
                all_results[file] = report
            else:
                print(f"\n❌ ҚАТЕ: {file} файлы табылмады!")
                print(f"   Қазіргі папкадағы файлдар: {os.listdir('.')}")
        except Exception as e:
            print(f"\n❌ ҚАТЕ: {file} өңдеу кезінде қате кетті: {e}")
            import traceback
            traceback.print_exc()
    
    # ҚОРЫТЫНДЫ
    if all_results:
        print("\n" + "="*80)
        print("📈 ҚОРЫТЫНДЫ ЕСЕП (SUMMARY REPORT):")
        print("="*80)
        
        summary_data = []
        for file, report in all_results.items():
            summary_data.append({
                'Файл': file,
                'Бастапқы жолдар': report['before_shape'][0],
                'Соңғы жолдар': report['after_shape'][0],
                'Жойылған жолдар': report['rows_removed'],
                'Қайталанатын жолдар': report['duplicates_removed'],
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
    
    print("\n" + "✨"*40)
    print("БАРЛЫҚ ТАПСЫРМАЛАР ОРЫНДАЛДЫ!")
    print("✨"*40)