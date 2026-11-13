# Universal Converter

Offline file converter with a clean, minimal desktop UI.  
Drop a file → pick a format → get the result. No internet, no registration, no ads.

---

## Quick start

```bash
# 1. Clone / unzip
cd universal_converter

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

---

## Project structure

```
universal_converter/
├── main.py                        Entry point
├── requirements.txt
├── app/
│   ├── config.py                  Constants, supported formats
│   ├── models/
│   │   └── job.py                 ConversionJob data model
│   ├── core/
│   │   ├── conversion_manager.py  Job queue + thread pool orchestration
│   │   ├── converters/
│   │   │   └── base.py            BaseConverter abstract interface
│   │   └── utils/
│   │       └── file_type.py       Extension → FileCategory detection
│   └── ui/
│       ├── styles/
│       │   └── main.qss           Global Qt stylesheet
│       ├── components/
│       │   └── drop_zone.py       Drag & Drop widget
│       └── views/
│           └── main_window.py     Main application window
├── resources/
│   ├── icons/
│   └── fonts/
└── tests/
    └── test_file_type.py
```

---

## Development roadmap

| Этап | Цель                              | Статус   |
|------|-----------------------------------|----------|
| 1    | Скелет проекта, архитектура MVC   | ✅ Done  |
| 2    | Главный экран, Drag & Drop UI     | 🔜 Next  |
| 3    | Конвертация изображений (Pillow)  | ⬜       |
| 4    | Видео, аудио, документы, данные   | ⬜       |
| 5    | Batch Mode, история, упаковка     | ⬜       |

---

## Adding a new converter

1. Create `app/core/converters/my_format.py`
2. Subclass `BaseConverter`, implement `can_handle()` and `convert()`
3. Register it in `main.py`:
   ```python
   manager.register_converter(MyFormatConverter())
   ```

That's it — no changes to the core required.
