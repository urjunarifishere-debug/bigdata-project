# Big Data — Деректерді өңдеу веб-сервисі
**Курс:** Big Data / Деректерді өңдеу | **Топ:** rpo1-24k

---

## Жобаны іске қосу

```bash
# 1. Виртуалды орта жасау
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Тәуелділіктерді орнату
pip install -r requirements.txt

# 3. Деректер базасын инициализациялау
python manage.py migrate

# 4. Суперпайдаланушы жасау (admin панелі үшін)
python manage.py createsuperuser

# 5. Серверді іске қосу
python manage.py runserver
```

Браузерде ашыңыз: http://127.0.0.1:8000

---

## Студентке тапсырма

Тек **`dataprocessor/utils/data_cleaner.py`** файлын толтырыңыз.

| Функция | Балл | Сипаттама |
|---|---|---|
| `get_shape()` | ТЗ 2.2 | Жол/баған санын қайтарады |
| `get_null_info()` | ТЗ 2.2 | Бос мәндер статистикасы |
| `get_numeric_stats()` | ТЗ 2.2 | min / max / mean |
| `get_top_values()` | ТЗ 2.2 | Ең жиі кездесетін мәндер |
| `clean_data()` | +5 қосымша | Деректерді тазалау |

Кем дегенде **3 функцияны** іске асыру міндетті!

---

## Жоба құрылымы

```
bigdata_project/
├── bigdata_config/          ← Django конфигурациясы
│   ├── settings.py
│   └── urls.py
├── dataprocessor/           ← Негізгі қосымша
│   ├── models.py            ← UploadedFile, ProcessingResult
│   ├── views.py             ← HTTP өңдеушілер
│   ├── forms.py             ← Жүктеу / опциялар формалары
│   ├── urls.py              ← URL маршруттары
│   ├── utils/
│   │   ├── data_cleaner.py  ← ★ СТУДЕНТ ТОЛТЫРАДЫ ★
│   │   ├── file_loader.py   ← Файлды DataFrame-ге айналдыру
│   │   └── result_exporter.py ← CSV/JSON экспорт
│   └── templates/
│       └── dataprocessor/   ← HTML шаблондар
├── media/uploads/           ← Жүктелген файлдар
├── requirements.txt
└── manage.py
```
