"""
Views — HTTP сұраулар өңдеушілері.

Маршруттар:
    /                    → index_view      — бас бет (жүктеу формасы)
    /process/<id>/       → process_view    — файлды өңдеу
    /results/<id>/       → results_view    — нәтижені браузерде көрсету
    /download/<id>/      → download_view   — нәтижені жүктеп алу
    /history/            → history_view    — жүктелген файлдар тарихы
"""

import time
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from .models import UploadedFile, ProcessingResult
from .forms import FileUploadForm, ProcessingOptionsForm
from .utils.file_loader import load_file_to_dataframe
from .utils.result_exporter import export_result_as_csv, export_result_as_json

# Студент іске асыратын функциялар:
from .utils.data_cleaner import (
    get_shape,
    get_null_info,
    get_numeric_stats,
    get_top_values,
    clean_data,
    analyze_changes,  # ✅ ҚОСЫЛДЫ
)


# ═══════════════════════════════════════════════════════════════════════
# БАС БЕТ — файл жүктеу
# ═══════════════════════════════════════════════════════════════════════

def index_view(request):
    """
    GET  → файл жүктеу формасын көрсетеді.
    POST → файлды қабылдап, дерекқорға сақтайды, process_view-ке бағыттайды.
    """
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file_obj = request.FILES['file']

            # UploadedFile моделіне сақтау
            record = UploadedFile(
                file=uploaded_file_obj,
                original_name=uploaded_file_obj.name,
                file_size=uploaded_file_obj.size,
            )
            record.save()

            messages.success(request, f'Файл сәтті жүктелді: {record.original_name}')
            # Өңдеу бетіне бағыттау
            return redirect('process', file_id=record.pk)
        else:
            messages.error(request, 'Файл жүктеу қатесі. Форманы тексеріңіз.')
    else:
        form = FileUploadForm()

    context = {
        'form': form,
        'recent_files': UploadedFile.objects.all()[:5],
    }
    return render(request, 'dataprocessor/index.html', context)


# ═══════════════════════════════════════════════════════════════════════
# ӨҢДЕУ — data_cleaner функцияларын шақыру
# ═══════════════════════════════════════════════════════════════════════

def process_view(request, file_id: int):
    """
    GET  → өңдеу параметрлерін таңдау формасын көрсетеді.
    POST → файлды оқып, data_cleaner функцияларын шақырып, нәтижені сақтайды.
    """
    file_record = get_object_or_404(UploadedFile, pk=file_id)

    if request.method == 'POST':
        options_form = ProcessingOptionsForm(request.POST)
        if options_form.is_valid():
            opts = options_form.cleaned_data
            start_time = time.time()

            try:
                # 1. Файлды жүктеп DataFrame-ге айналдыру
                file_path = file_record.file.path
                df = load_file_to_dataframe(file_path, file_record.file_type)

                # Түпнұсқаны сақтау (өзгерістерді талдау үшін)
                original_df = df.copy()
                
                # Деректерді тазалау
                df, detailed_changes = clean_data(df)

                # ✅ ӨЗГЕРІСТЕРДІ ТАЛДАУ (analyze_changes шақыру)
                changes = analyze_changes(original_df, df, detailed_changes)

                # 2. Нәтиже объектін дайындау
                result_data = {}

                # ТЗ 2.2 — Жол/баған саны
                if opts.get('show_shape'):
                    result_data['shape'] = get_shape(df)

                # ТЗ 2.2 — Null мәндер
                if opts.get('show_nulls'):
                    result_data['null_info'] = get_null_info(df)

                # ТЗ 2.2 — Сандық статистика
                if opts.get('show_stats'):
                    result_data['numeric_stats'] = get_numeric_stats(df)

                # ТЗ 2.2 — Top-N мәндер
                if opts.get('show_top_values'):
                    top_n = opts.get('top_n') or 5
                    result_data['top_values'] = get_top_values(df, top_n=top_n)

                elapsed = time.time() - start_time

                # 3. ProcessingResult дерекқорға сақтау
                shape = result_data.get('shape', {})
                null_info = result_data.get('null_info', {})
                numeric = result_data.get('numeric_stats', {})
                top_vals = result_data.get('top_values', {})

                ProcessingResult.objects.update_or_create(
                    uploaded_file=file_record,
                    defaults={
                        'row_count':      shape.get('row_count'),
                        'column_count':   shape.get('column_count'),
                        'column_names':   shape.get('column_names'),
                        'null_counts':    null_info.get('null_counts'),
                        'total_nulls':    null_info.get('total_nulls'),
                        'numeric_stats':  numeric or None,
                        'top_values':     top_vals or None,
                        'processing_time': round(elapsed, 3),
                        'error_message':  '',
                    }
                )

                file_record.is_processed = True
                file_record.save()

                # ✅ ӨЗГЕРІСТЕРДІ СЕССИЯҒА САҚТАУ (results_view-де көрсету үшін)
                request.session['changes'] = changes

                messages.success(request, f'Өңдеу аяқталды! ({elapsed:.2f} сек)')
                return redirect('results', file_id=file_id)

            except NotImplementedError as e:
                messages.error(request, f'Функция әлі іске асырылмаған: {e}')
            except Exception as e:
                # Қатені дерекқорға жазу
                ProcessingResult.objects.update_or_create(
                    uploaded_file=file_record,
                    defaults={'error_message': str(e)}
                )
                messages.error(request, f'Өңдеу кезінде қате: {e}')

    else:
        options_form = ProcessingOptionsForm()

    context = {
        'file_record': file_record,
        'options_form': options_form,
    }
    return render(request, 'dataprocessor/process.html', context)


# ═══════════════════════════════════════════════════════════════════════
# НӘТИЖЕЛЕР — браузерде көрсету
# ═══════════════════════════════════════════════════════════════════════

def results_view(request, file_id: int):
    """
    Өңдеу нәтижесін браузерде HTML кестелер / диаграммалар түрінде көрсетеді.
    ТЗ 2.3 — Өңдеу нәтижесі браузерде көрсетіледі.
    """
    file_record = get_object_or_404(UploadedFile, pk=file_id)
    result = get_object_or_404(ProcessingResult, uploaded_file=file_record)
    
    # ✅ СЕССИЯДАН ӨЗГЕРІСТЕРДІ АЛУ
    changes = request.session.get('changes', None)

    context = {
        'file_record': file_record,
        'result': result,
        'changes': changes,  # ✅ ҚОСЫЛДЫ
        'download_form': ProcessingOptionsForm(),
    }
    return render(request, 'dataprocessor/results.html', context)


# ═══════════════════════════════════════════════════════════════════════
# ЖҮКТЕП АЛУ — CSV немесе JSON
# ═══════════════════════════════════════════════════════════════════════

def download_view(request, file_id: int):
    """
    Нәтижені CSV немесе JSON форматында жүктеп алуды қамтамасыз етеді.
    ТЗ 2.3 — Нәтижені жүктеп алуға болады.

    Query параметрі: ?format=csv немесе ?format=json
    """
    file_record = get_object_or_404(UploadedFile, pk=file_id)
    result = get_object_or_404(ProcessingResult, uploaded_file=file_record)

    fmt = request.GET.get('format', 'csv').lower()

    if fmt == 'json':
        content = export_result_as_json(result)
        content_type = 'application/json'
        filename = f'result_{file_record.pk}.json'
    else:
        content = export_result_as_csv(result)
        content_type = 'text/csv; charset=utf-8'
        filename = f'result_{file_record.pk}.csv'

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ═══════════════════════════════════════════════════════════════════════
# ТАРИХ — барлық жүктелген файлдар
# ═══════════════════════════════════════════════════════════════════════

def history_view(request):
    """Жүктелген файлдар тарихын тізімдейді."""
    files = UploadedFile.objects.all()
    return render(request, 'dataprocessor/history.html', {'files': files})