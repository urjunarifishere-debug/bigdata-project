import pandas as pd
import numpy as np

def get_shape(df):
    """
    Деректер көлемін қайтарады (жолдар мен бағандар саны)
    
    Args:
        df (pd.DataFrame): Входной DataFrame
        
    Returns:
        dict: Словарь с row_count, column_count, column_names
    """
    return {
        'row_count': df.shape[0],
        'column_count': df.shape[1],
        'column_names': df.columns.tolist()
    }


def get_null_info(df):
    """
    Бос мәндер туралы ақпарат қайтарады
    
    Args:
        df (pd.DataFrame): Входной DataFrame
        
    Returns:
        dict: Словарь с null_counts, total_nulls, null_percent
    """
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    null_percent = (null_counts / len(df) * 100).round(2).to_dict()
    
    return {
        'null_counts': null_counts.to_dict(),
        'total_nulls': int(total_nulls),
        'null_percent': null_percent
    }


def get_numeric_stats(df):
    """
    Сандық бағандардың статистикасын қайтарады (min, max, mean)
    
    Args:
        df (pd.DataFrame): Входной DataFrame
        
    Returns:
        dict: Словарь со статистикой по числовым столбцам
    """
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return {'stats': {}, 'numeric_columns': []}
    
    stats = {}
    for col in numeric_df.columns:
        stats[col] = {
            'min': float(numeric_df[col].min()) if not pd.isna(numeric_df[col].min()) else None,
            'max': float(numeric_df[col].max()) if not pd.isna(numeric_df[col].max()) else None,
            'mean': round(float(numeric_df[col].mean()), 2) if not pd.isna(numeric_df[col].mean()) else None
        }
    
    return {
        'stats': stats,
        'numeric_columns': numeric_df.columns.tolist()
    }


def get_top_values(df, top_n=5):
    """
    Санаттық бағандардағы ең көп кездесетін мәндерді қайтарады
    
    Args:
        df (pd.DataFrame): Входной DataFrame
        top_n (int): Количество топ значений (по умолчанию 5)
        
    Returns:
        dict: Словарь с топ значениями для каждого столбца
    """
    top_values = {}
    
    for col in df.columns:
        # Получаем топ-N значений для каждого столбца
        value_counts = df[col].value_counts(dropna=True).head(top_n)
        
        if len(value_counts) > 0:
            top_values[col] = [
                {'value': str(val), 'count': int(count)} 
                for val, count in value_counts.items()
            ]
        else:
            top_values[col] = []
    
    return {'top_values': top_values}


def clean_data(df):
    """
    Деректерді тазалау (барлық 4 операция)
    
    Выполняемые операции:
    1. Нормализация названий столбцов (нижний регистр)
    2. Удаление дублирующихся строк
    3. Удаление пробелов в строковых значениях
    4. Заполнение пропусков в числовых столбцах медианой
    
    Args:
        df (pd.DataFrame): Входной DataFrame для очистки
        
    Returns:
        tuple: (Очищенный DataFrame, список изменений)
    """
    df_clean = df.copy()
    changes = []
    
    original_columns = df_clean.columns.tolist()
    df_clean.columns = df_clean.columns.str.strip().str.lower()
    new_columns = df_clean.columns.tolist()
    
    duplicates_mask = df_clean.duplicated(keep='first')
    duplicate_indices = df_clean[duplicates_mask].index.tolist()
    
    df_clean = df_clean.drop_duplicates()
    
    for col in df_clean.select_dtypes(include=['object']).columns:
        for idx in df_clean.index:
            original_val = df_clean.at[idx, col]
            if isinstance(original_val, str):
                cleaned_val = original_val.strip()
                if cleaned_val == '':
                    cleaned_val = np.nan
                if cleaned_val != original_val:
                    changes.append({
                        'row_index': idx,
                        'column': col,
                        'original_value': original_val,
                        'cleaned_value': cleaned_val,
                        'change_type': 'trim_whitespace' if cleaned_val != np.nan else 'empty_to_nan'
                    })
                df_clean.at[idx, col] = cleaned_val
    
    for col in df_clean.select_dtypes(include=[np.number]).columns:
        if df_clean[col].isnull().any():
            median_val = df_clean[col].median()
            null_mask = df_clean[col].isnull()
            for idx in df_clean[null_mask].index:
                changes.append({
                    'row_index': idx,
                    'column': col,
                    'original_value': np.nan,
                    'cleaned_value': median_val,
                    'change_type': 'fill_null_median'
                })
            df_clean[col] = df_clean[col].fillna(median_val)
    
    return df_clean, changes


def analyze_changes(original_df, cleaned_df, changes_list=None):
    """
    Анализирует изменения между исходным и очищенным DataFrame
    
    Args:
        original_df (pd.DataFrame): Исходный DataFrame
        cleaned_df (pd.DataFrame): Очищенный DataFrame
        changes_list (list): Список конкретных изменений (опционально)
    
    Returns:
        dict: Словарь с информацией об изменениях
    """
    changes = {
        'original_rows': len(original_df),
        'cleaned_rows': len(cleaned_df),
        'rows_removed': len(original_df) - len(cleaned_df),
        'original_columns': len(original_df.columns),
        'cleaned_columns': len(cleaned_df.columns),
        'columns_renamed': not all(original_df.columns.str.lower() == cleaned_df.columns),
        'original_nulls': int(original_df.isnull().sum().sum()),
        'cleaned_nulls': int(cleaned_df.isnull().sum().sum()),
        'nulls_filled': int(original_df.isnull().sum().sum() - cleaned_df.isnull().sum().sum()),
        'summary': [],
        'changed_rows': changes_list or [] 
    }
    
    if changes['rows_removed'] > 0:
        changes['summary'].append(f"Удалено {changes['rows_removed']} дублирующихся строк")
    
    if changes['nulls_filled'] > 0:
        changes['summary'].append(f"Заполнено {changes['nulls_filled']} пропущенных значений")
    
    if changes['columns_renamed']:
        changes['summary'].append("Названия столбцов приведены к нижнему регистру")
    
    if not changes['summary']:
        changes['summary'].append("Изменений не обнаружено")
    
    return changes