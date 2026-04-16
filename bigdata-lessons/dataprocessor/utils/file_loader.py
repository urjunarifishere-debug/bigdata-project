"""
Файлды жүктеу және DataFrame-ге айналдыру утилитасы.

Студент осы модульді өзгертпеуі керек — бұл базалық инфрақұрылым.
"""

import pandas as pd
import json


def load_file_to_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
    """
    Дискте сақталған файлды оқып, pandas DataFrame қайтарады.

    Параметрлер:
        file_path (str): Файлдың толық жолы
        file_type (str): 'csv', 'json', 'txt', 'xlsx'

    Қайтарады:
        pd.DataFrame — файл мазмұны

    Ерекше жағдайлар:
        ValueError — қолдауға алынбаған формат
        Exception  — файл оқу қатесі
    """
    loaders = {
        'csv':  _load_csv,
        'txt':  _load_csv,   # TXT де CSV сияқты оқылады
        'json': _load_json,
        'xlsx': _load_xlsx,
    }

    loader = loaders.get(file_type)
    if loader is None:
        raise ValueError(f'Қолдауға алынбаған файл типі: {file_type}')

    return loader(file_path)


# -----------------------------------------------------------------------
# Жеке жүктеу функциялары
# -----------------------------------------------------------------------

def _load_csv(file_path: str) -> pd.DataFrame:
    """CSV / TXT файлын жүктейді. Автоматты delimiter анықтайды."""
    try:
        return pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, sep=None, engine='python', encoding='cp1251')


def _load_json(file_path: str) -> pd.DataFrame:
    """JSON файлын жүктейді. Тізім немесе кілт-мән форматын қолдайды."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        return pd.DataFrame([data])
    else:
        raise ValueError('JSON форматы қолдауға алынбайды (тізім немесе объект болуы тиіс).')


def _load_xlsx(file_path: str) -> pd.DataFrame:
    """Excel (XLSX) файлын жүктейді. Бірінші парақты оқиды."""
    return pd.read_excel(file_path, engine='openpyxl')
