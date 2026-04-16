"""
URL маршруттары — dataprocessor қосымшасы.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Бас бет: файл жүктеу формасы
    path('', views.index_view, name='index'),

    # Өңдеу параметрлерін таңдау және өңдеуді іске қосу
    path('process/<int:file_id>/', views.process_view, name='process'),

    # Нәтижені браузерде көрсету
    path('results/<int:file_id>/', views.results_view, name='results'),

    # Нәтижені жүктеп алу (?format=csv немесе ?format=json)
    path('download/<int:file_id>/', views.download_view, name='download'),

    # Жүктелген файлдар тарихы
    path('history/', views.history_view, name='history'),
]
