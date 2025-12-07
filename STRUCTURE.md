# Структура проекта Makenanalog

## Обзор

Проект организован в модульную структуру для лучшей поддерживаемости и расширяемости.

## Иерархия файлов

```
makenanalog/
├── src/                          # Основной код приложения
│   ├── __init__.py              # Инициализация пакета и экспорт основных классов
│   ├── config.py                # Класс Config - управление конфигурацией и профилями
│   ├── file_manager.py          # Класс LocalFileManager - работа с файловой системой
│   ├── prompt_generator.py      # Класс PromptGenerator - генерация промптов (Gemini/OpenAI/Grok)
│   ├── image_generator.py       # Класс ImageGenerator - генерация изображений (Wavespeed)
│   ├── caption_generator.py    # Класс CaptionGenerator - генерация captions для LoRA
│   ├── dataset_creator.py       # Класс DatasetCreator - оркестрация процесса создания датасета
│   ├── interactive_menu.py      # Интерактивное меню и функции работы с профилями
│   └── utils.py                 # Вспомогательные функции (выбор языка и т.д.)
│
├── main.py                       # Точка входа приложения
├── dataset_creation.py           # Файл обратной совместимости (импортирует из src/)
├── i18n.py                       # Система локализации (русский/английский)
│
├── config.example.json          # Пример конфигурационного файла
├── config.json                   # Основной конфигурационный файл (создается автоматически)
│
├── profiles/                     # Профили настроек (создается автоматически)
│   └── *.json                   # Файлы профилей
│
├── output/                       # Выходные файлы (создается автоматически)
│   ├── lora_dataset/            # Сгенерированные изображения и captions
│   └── *.zip                    # Архивы датасетов
│
├── Sample Dataset/               # Примеры изображений для обработки
│   ├── normal/                  # Обычный контент
│   └── nsfw/                    # NSFW контент
│
├── Influencer Reference Images/  # Референсные изображения для промптов
│
├── requirements.txt              # Зависимости Python
├── LICENSE                       # Лицензия проекта
│
├── README.md                     # Основной README (на русском и английском)
├── README_RU.md                  # Подробная документация на русском
├── README_EN.md                  # Подробная документация на английском
└── STRUCTURE.md                  # Этот файл - описание структуры проекта
```

## Описание модулей

### `src/config.py`
- **Config** - класс для управления конфигурацией приложения
- Загрузка/сохранение базовой конфигурации из `config.json`
- Управление профилями (создание, загрузка, сохранение)
- Хранение API ключей и настроек моделей

### `src/file_manager.py`
- **LocalFileManager** - класс для работы с локальной файловой системой
- Список изображений из папок с поддержкой NSFW/normal разделения
- Чтение файлов и определение MIME типов
- Автоматическое определение типа контента по пути

### `src/prompt_generator.py`
- **PromptGenerator** - класс для генерации промптов
- Поддержка провайдеров: Gemini, OpenAI, Grok
- Специальные шаблоны промптов для разных моделей Wavespeed
- Отдельный шаблон для Grok с поддержкой NSFW контента

### `src/image_generator.py`
- **ImageGenerator** - класс для генерации изображений
- Интеграция с Wavespeed API
- Поддержка различных моделей (Seedream, Nano Banana, и т.д.)
- Обработка ошибок и retry логика

### `src/caption_generator.py`
- **CaptionGenerator** - класс для генерации captions для LoRA
- Поддержка OpenAI и Grok провайдеров
- Генерация captions с учетом trigger name

### `src/dataset_creator.py`
- **DatasetCreator** - основной класс оркестрации
- Координация работы всех компонентов
- Динамическое применение настроек в зависимости от типа контента (NSFW/normal)
- Создание zip архивов датасетов

### `src/interactive_menu.py`
- **interactive_menu()** - интерактивное меню для выбора настроек
- **select_or_create_profile()** - выбор или создание профиля
- **save_profile_menu()** - сохранение текущих настроек в профиль
- Поддержка rich/inquirer для красивого интерфейса

### `src/utils.py`
- **select_language()** - функция выбора языка интерфейса
- Вспомогательные утилиты

## Точки входа

### `main.py`
Основная точка входа приложения. Запускается командой:
```bash
python main.py
```

### `dataset_creation.py`
Файл обратной совместимости для старых скриптов. Импортирует все из `src/` и может быть запущен напрямую:
```bash
python dataset_creation.py
```

## Импорты

### Из корня проекта
```python
from src import Config, DatasetCreator, interactive_menu
```

### Из модулей напрямую
```python
from src.config import Config
from src.dataset_creator import DatasetCreator
```

### Обратная совместимость
```python
# Старый способ (все еще работает)
from dataset_creation import Config, DatasetCreator
```

## Расширение проекта

Для добавления новых функций:

1. **Новый провайдер AI**: Добавьте метод в `src/prompt_generator.py`
2. **Новая модель генерации**: Добавьте поддержку в `src/image_generator.py`
3. **Новая функция**: Создайте новый модуль в `src/` и добавьте экспорт в `src/__init__.py`

## Зависимости

Все зависимости указаны в `requirements.txt`. Основные:
- `google-generativeai` - для Gemini
- `openai` - для OpenAI и Grok
- `requests` - для HTTP запросов
- `rich` - для красивого вывода (опционально)
- `inquirer` - для интерактивного меню (опционально)

