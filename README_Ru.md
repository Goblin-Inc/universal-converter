# Universal Converter

> 🌐 **Язык:** [English (README.md)](README.md) | **Русский**

Офлайн десктопный конвертер файлов с минималистичным интерфейсом на **Python** и **PySide6**.  
Перетащите файл → выберите формат → получите результат. Без интернета, регистрации и рекламы.

---

## Быстрый старт

```bash
# 1. Клонируйте репозиторий
cd universal_converter

# 2. Создайте виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Запустите приложение
python main.py
```

---

## Структура проекта

```
universal_converter/
├── main.py                        Точка входа
├── requirements.txt
├── app/
│   ├── config.py                  Константы и поддерживаемые форматы
│   ├── models/
│   │   └── job.py                 Модель задачи конвертации (ConversionJob)
│   ├── core/
│   │   ├── conversion_manager.py  Очередь задач и пул потоков
│   │   ├── converters/
│   │   │   └── base.py            Абстрактный базовый класс BaseConverter
│   │   └── utils/
│   │       └── file_type.py       Определение категории файла по расширению
│   └── ui/
│       ├── styles/
│       │   └── main.qss           Глобальная таблица стилей Qt
│       ├── components/
│       │   └── drop_zone.py       Виджет Drag & Drop
│       └── views/
│           └── main_window.py     Главное окно приложения
├── resources/
│   ├── icons/
│   └── fonts/
└── tests/
    └── test_file_type.py
```

---

## План разработки (Roadmap)

| Этап | Цель                              | Статус   |
|------|-----------------------------------|----------|
| 1    | Скелет проекта, архитектура MVC   | ✅ Готово |
| 2    | Главный экран, Drag & Drop UI     | 🔜 Далее |
| 3    | Конвертация изображений (Pillow)  | ⬜       |
| 4    | Видео, аудио, документы, данные   | ⬜       |
| 5    | Пакетный режим, история, сборка   | ⬜       |

---

## Добавление нового конвертера

1. Создайте `app/core/converters/my_format.py`
2. Унаследуйте `BaseConverter`, реализуйте методы `can_handle()` и `convert()`
3. Зарегистрируйте его в `main.py`:
   ```python
   manager.register_converter(MyFormatConverter())
   ```
