#!/usr/bin/env python3
"""
Dataset Creation Bulk - Python аналог Make.com workflow
Поддерживает локальное хранение, выбор между Gemini/OpenAI и Wavespeed

Этот файл предоставляет обратную совместимость для старых скриптов.
Новый модульный код находится в папке src/:
- src/config.py - класс Config
- src/file_manager.py - класс LocalFileManager
- src/prompt_generator.py - класс PromptGenerator
- src/image_generator.py - класс ImageGenerator
- src/caption_generator.py - класс CaptionGenerator
- src/dataset_creator.py - класс DatasetCreator
- src/interactive_menu.py - интерактивное меню
- src/utils.py - вспомогательные функции
- main.py - точка входа

Для запуска используйте: python main.py
"""

# Импортируем все классы и функции из новых модулей для обратной совместимости
from src import (
    Config,
    LocalFileManager,
    PromptGenerator,
    ImageGenerator,
    CaptionGenerator,
    DatasetCreator,
    interactive_menu,
    select_or_create_profile,
    save_profile_menu,
    select_language
)

# Импортируем i18n для обратной совместимости
try:
    from i18n import get_i18n, set_language
except ImportError:
    def get_i18n():
        class SimpleI18n:
            def t(self, key, **kwargs):
                return key
        return SimpleI18n()
    def set_language(lang):
        return True

# Экспортируем все для обратной совместимости
__all__ = [
    'Config',
    'LocalFileManager',
    'PromptGenerator',
    'ImageGenerator',
    'CaptionGenerator',
    'DatasetCreator',
    'interactive_menu',
    'select_or_create_profile',
    'save_profile_menu',
    'select_language',
    'get_i18n',
    'set_language',
]

# Если файл запущен напрямую, используем main.py
if __name__ == '__main__':
    from main import main
    main()
