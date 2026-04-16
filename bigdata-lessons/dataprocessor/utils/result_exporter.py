"""
Нәтижені CSV немесе JSON форматында экспорттау утилитасы.

ТЗ 2.3 — Нәтижені жүктеп алуға болады (CSV немесе JSON форматында)

Студент осы модульді өзгертпеуі керек.
"""

import json
import csv
import io
from dataprocessor.models import ProcessingResult


def export_result_as_csv(result: ProcessingResult) -> str:
    """
    ProcessingResult объектін CSV мәтіні ретінде қайтарады.

    Қайтарады:
        str — CSV форматындағы нәтиже
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Тақырып
    writer.writerow(['Параметр', 'Мән'])
    writer.writerow(['Файл атауы', result.uploaded_file.original_name])
    writer.writerow(['Жол саны', result.row_count])
    writer.writerow(['Баған саны', result.column_count])
    writer.writerow(['Жалпы null саны', result.total_nulls])
    writer.writerow([])

    # Null бойынша
    if result.null_counts:
        writer.writerow(['--- NULL МӘНДЕР ---', ''])
        writer.writerow(['Баған', 'Null саны'])
        for col, cnt in result.null_counts.items():
            writer.writerow([col, cnt])
        writer.writerow([])

    # Сандық статистика
    if result.numeric_stats:
        writer.writerow(['--- САНДЫҚ СТАТИСТИКА ---', ''])
        writer.writerow(['Баған', 'Min', 'Max', 'Орташа'])
        for col, stats in result.numeric_stats.get('stats', {}).items():
            writer.writerow([col, stats.get('min'), stats.get('max'), stats.get('mean')])
        writer.writerow([])

    # Top мәндер
    if result.top_values:
        writer.writerow(['--- TOP МӘНДЕР ---', ''])
        for col, vals in result.top_values.get('top_values', {}).items():
            writer.writerow([f'{col} — мән', f'{col} — саны'])
            for item in vals:
                writer.writerow([item.get('value'), item.get('count')])
            writer.writerow([])

    return output.getvalue()


def export_result_as_json(result: ProcessingResult) -> str:
    """
    ProcessingResult объектін JSON мәтіні ретінде қайтарады.

    Қайтарады:
        str — JSON форматындағы нәтиже
    """
    data = {
        'file': result.uploaded_file.original_name,
        'row_count': result.row_count,
        'column_count': result.column_count,
        'column_names': result.column_names,
        'null_info': {
            'total_nulls': result.total_nulls,
            'per_column': result.null_counts,
        },
        'numeric_stats': result.numeric_stats,
        'top_values': result.top_values,
        'processing_time_sec': result.processing_time,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
