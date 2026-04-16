from django.contrib import admin
from .models import UploadedFile, ProcessingResult


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'file_type', 'file_size', 'is_processed', 'uploaded_at')
    list_filter = ('file_type', 'is_processed')
    search_fields = ('original_name',)
    readonly_fields = ('uploaded_at', 'file_size', 'file_type')


@admin.register(ProcessingResult)
class ProcessingResultAdmin(admin.ModelAdmin):
    list_display = ('uploaded_file', 'row_count', 'column_count', 'total_nulls', 'processing_time', 'processed_at')
    readonly_fields = ('processed_at',)
