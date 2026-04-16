"""
Django формалары.
"""

from django import forms
from django.conf import settings
import os


class FileUploadForm(forms.Form):
    """Файл жүктеу формасы."""

    file = forms.FileField(
        label='Файл таңдаңыз',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.json,.txt,.xlsx',
        }),
        help_text='Рұқсат берілген форматтар: CSV, JSON, TXT, XLSX. Макс. өлшем: 100 МБ'
    )

    def clean_file(self):
        """
        Файлды тексереді:
          1. Өлшемі 100 МБ-тан аспауы керек
          2. Кеңейтімі рұқсат берілгендер тізімінде болуы керек
        """
        uploaded_file = self.cleaned_data.get('file')

        if not uploaded_file:
            raise forms.ValidationError('Файл таңдалмады.')

        # --- 1. Өлшемін тексеру ---
        max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE  # 100 МБ
        if uploaded_file.size > max_size:
            raise forms.ValidationError(
                f'Файл өлшемі тым үлкен: {uploaded_file.size // (1024*1024)} МБ. '
                f'Максимум {max_size // (1024*1024)} МБ рұқсат берілген.'
            )

        # --- 2. Кеңейтімін тексеру ---
        _, ext = os.path.splitext(uploaded_file.name)
        if ext.lower() not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            raise forms.ValidationError(
                f'"{ext}" кеңейтімі қолдауға алынбайды. '
                f'Рұқсат берілгендер: {", ".join(settings.ALLOWED_UPLOAD_EXTENSIONS)}'
            )

        return uploaded_file


class ProcessingOptionsForm(forms.Form):
    """Қандай өңдеу функцияларын орындау керектігін таңдау формасы."""

    # ТЗ 2.2 бойынша студент кем дегенде 3-ін іске асыруы тиіс
    show_shape = forms.BooleanField(
        label='Жол/баған санын шығару',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    show_nulls = forms.BooleanField(
        label='Бос мәндерді (null) анықтау',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    show_stats = forms.BooleanField(
        label='Сандық статистика (min, max, орташа)',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    show_top_values = forms.BooleanField(
        label='Ең жиі кездесетін мәндер (Top-N)',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    top_n = forms.IntegerField(
        label='Top-N саны',
        initial=5,
        min_value=1,
        max_value=50,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px'}),
    )

    # Нәтижені жүктеп алу форматы
    download_format = forms.ChoiceField(
        label='Нәтижені жүктеу форматы',
        choices=[('csv', 'CSV'), ('json', 'JSON')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
