#!/usr/bin/env python3
"""
Система локализации (i18n) для проекта
Поддерживает русский и английский языки
"""

import os
import json
from typing import Dict, Optional

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['ru', 'en']
DEFAULT_LANGUAGE = 'ru'

# Тексты локализации
TRANSLATIONS = {
    'ru': {
        # Общие
        'app_name': 'Dataset Creation - Создание датасетов для LoRA',
        'error': 'Ошибка',
        'success': 'Успешно',
        'warning': 'Предупреждение',
        'info': 'Информация',
        'yes': 'Да',
        'no': 'Нет',
        'skip': 'Пропустить',
        'continue': 'Продолжить',
        'cancel': 'Отмена',
        'save': 'Сохранить',
        'load': 'Загрузить',
        'delete': 'Удалить',
        'back': 'Назад',
        'next': 'Далее',
        'finish': 'Завершить',
        'select': 'Выбрать',
        'enter': 'Введите',
        'or': 'или',
        
        # Файлы и папки
        'file_not_found': 'Файл не найден',
        'folder_not_found': 'Папка не найдена',
        'file_saved': 'Файл сохранен',
        'folder_created': 'Папка создана',
        'file_exists': 'Файл уже существует',
        
        # API и провайдеры
        'api_key_missing': 'API ключ не установлен',
        'api_key_invalid': 'API ключ недействителен',
        'provider_not_available': 'Провайдер недоступен',
        'request_failed': 'Запрос не выполнен',
        'rate_limit_exceeded': 'Превышен лимит запросов',
        
        # Генерация
        'generating_prompt': 'Генерация промпта...',
        'generating_image': 'Генерация изображения...',
        'generating_caption': 'Генерация подписи...',
        'processing': 'Обработка',
        'completed': 'Завершено',
        'failed': 'Не удалось',
        
        # Меню
        'interactive_menu_title': 'Dataset Creation - Интерактивная настройка',
        'select_option': 'Выберите опцию',
        'select_settings': 'Выберите настройки (Enter для пропуска, будут использованы значения по умолчанию):',
        'current_value': 'Текущее значение',
        'not_selected': 'не выбрано',
        'your_choice': 'Ваш выбор',
        'press_enter_to_skip': 'Нажмите Enter для пропуска',
        'invalid_choice': 'Неверный выбор',
        'selected': 'Выбрано',
        'using_value': 'Используется значение',
        'settings_selected': 'Настройки выбраны!',
        'final_settings': 'Итоговые настройки:',
        'processing_mode': 'Режим обработки',
        'image_generation_provider': 'Провайдер для генерации изображений/видео',
        'wavespeed_model': 'Модель Wavespeed',
        'resolution': 'Разрешение для Wavespeed',
        'caption_generation': 'Генерация подписей (captions) для LoRA обучения',
        'trigger_name_prompt': 'Имя персонажа (trigger name) для LoRA',
        'openai_caption_model': 'Модель OpenAI для генерации captions',
        
        # Настройки
        'ai_provider': 'AI провайдер для генерации промптов',
        'image_provider': 'Провайдер генерации изображений',
        'prompt_template': 'Шаблон промпта',
        'model': 'Модель',
        'resolution': 'Разрешение',
        'output_format': 'Формат вывода',
        'trigger_name': 'Имя триггера (trigger name)',
        'generate_captions': 'Генерировать подписи (captions)',
        
        # Провайдеры
        'gemini': 'Gemini',
        'openai': 'OpenAI',
        'wavespeed': 'Wavespeed',
        
        # Шаблоны
        'bulk': 'Bulk (массовая обработка)',
        'detailed': 'Detailed (детальная обработка)',
        
        # Профили
        'profile': 'Профиль',
        'profile_management': 'Управление профилями',
        'profile_name': 'Имя профиля',
        'save_profile': 'Сохранить настройки как профиль',
        'load_profile': 'Загрузить профиль',
        'profile_saved': 'Профиль сохранен',
        'profile_loaded': 'Профиль загружен',
        'profile_not_found': 'Профиль не найден',
        'profile_exists': 'Профиль уже существует',
        'found_profiles': 'Найдено {count} сохраненных профилей:',
        'create_new_profile': 'Создать новый профиль',
        'skip_use_temporary': 'Пропустить (использовать временные настройки)',
        'no_profiles_saved': 'Сохраненных профилей нет.',
        'selected_profile': 'Выбран профиль: {name}',
        'invalid_choice_create_new': 'Неверный выбор, создаем новый профиль',
        'save_profile_title': 'Сохранение профиля',
        'want_to_save_profile': 'Хотите сохранить эти настройки как профиль?',
        'yes_save': 'Да, сохранить',
        'no_skip': 'Нет, пропустить',
        'profile_already_exists': "Профиль '{name}' уже существует!",
        'overwrite_existing': 'Перезаписать существующий профиль',
        'cancel_saving': 'Отменить сохранение',
        'saving_cancelled': 'Сохранение отменено',
        'enter_profile_description': 'Введите описание профиля (опционально, Enter для пропуска):',
        'profile_description_example': 'Пример: {example}',
        'profile_created': "Профиль '{name}' создан!",
        'profile_updated': "Профиль '{name}' обновлен!",
        'profile_path': 'Путь: {path}',
        'error_saving_profile': 'Ошибка при сохранении профиля: {error}',
        'settings_not_saved': 'Настройки не сохранены (будут использованы только для этого запуска)',
        
        # Результаты
        'images_processed': 'Изображений обработано',
        'images_generated': 'Изображений сгенерировано',
        'captions_generated': 'Подписей сгенерировано',
        'zip_created': 'Zip архив создан',
        'output_folder': 'Папка результатов',
        
        # Процесс обработки
        'loading_ref_images': 'Загрузка референсных изображений...',
        'found_ref_images': 'Найдено {count} референсных изображений',
        'loading_sample_images': 'Загрузка sample изображений...',
        'mode_detailed': 'Режим: detailed (обработка одного изображения)',
        'mode_detailed_corresponds': 'Соответствует: Dataset Image Generation NanoBanana 2 (getFile для одного файла)',
        'mode_bulk': 'Режим: bulk (массовая обработка до {limit} изображений)',
        'mode_bulk_corresponds': 'Соответствует: Dataset Creation Bulk Gemini (listAllFiles с limit={limit})',
        'found_sample_images': 'Найдено {count} sample изображений',
        'found_sample_images_for_processing': 'Найдено {count} sample изображений для обработки',
        'image_not_selected': 'Изображение не выбрано, обработка отменена',
        'image_selected': 'Выбрано изображение: {name}',
        'processing_image': 'Обработка {current}/{total}: {name}',
        'generating_prompt': 'Генерация промпта...',
        'prompt_generated': 'Промпт сгенерирован ({length} символов)',
        'generating_image': 'Генерация изображения через {provider} ({model})...',
        'image_saved': 'Изображения сохранено: {path}',
        'video_saved': 'Видео сохранено: {path}',
        'generating_captions': 'Генерация подписей (captions) для LoRA обучения...',
        'generating_caption_for': 'Генерация подписи для {name}...',
        'caption_saved': 'Подпись сохранена: {name}',
        'creating_zip': 'Создание zip архива: {name}...',
        'zip_created_path': 'Zip архив создан: {path}',
        'total_files': 'Всего файлов: {images} изображений + {captions} подписей',
        'all_files_saved_in': 'Все файлы сохранены в: {path}',
        'processing_completed': 'Обработка завершена! Результаты сохранены в: {path}',
        'caption_generation_skipped': 'Генерация подписей будет пропущена',
        'caption_generator_not_initialized': 'Генератор подписей не инициализирован',
        'error_generating_caption_for': 'Ошибка при генерации подписи для {name}: {error}',
        
        # Ошибки Wavespeed
        'wavespeed_timeout_error': 'Таймаут при запросе к Wavespeed API (таймаут: {timeout} секунд). Сервер не ответил вовремя. Попробуйте позже или уменьшите размер изображений.',
        'wavespeed_request_error': 'Ошибка при запросе к Wavespeed: {error}',
        'wavespeed_api_error': 'Wavespeed API вернул ошибку: {error}',
        'server_response': 'Ответ сервера',
        'unknown_error': 'Неизвестная ошибка',
        
        # Выбор изображения
        'image_selection_title': 'Выбор изображения из Sample Dataset',
        'image_selection_available': 'Доступные изображения',
        
        # Ошибки
        'error_loading_config': 'Ошибка загрузки конфигурации',
        'error_saving_config': 'Ошибка сохранения конфигурации',
        'error_processing_image': 'Ошибка обработки изображения',
        'error_generating_prompt': 'Ошибка генерации промпта',
        'error_generating_image': 'Ошибка генерации изображения',
        'error_generating_caption': 'Ошибка генерации подписи',
        
        # Тестирование
        'testing_models': 'Тестирование моделей',
        'testing_captions': 'Тестирование генерации captions',
        'test_successful': 'Тест успешен',
        'test_failed': 'Тест не пройден',
        
        # Информация
        'select_language': 'Выберите язык / Select language',
        'language_set': 'Язык установлен',
        
        # Описания AI провайдеров
        'gemini_description_1': 'Быстрая генерация промптов',
        'gemini_description_2': 'Бесплатный с лимитами (60 запросов/мин)',
        'gemini_description_3': 'Хорошее качество анализа изображений',
        'gemini_description_4': 'Поддержка мультимодальных запросов',
        'gemini_description_5': 'Есть лимиты на количество запросов',
        'gemini_description_6': 'Рекомендуется для: начала работы, тестирования, экономии',
        'openai_description_1': 'Высокая точность анализа',
        'openai_description_2': 'Лучшее понимание контекста',
        'openai_description_3': 'Более структурированные ответы',
        'openai_description_4': 'Нет жестких лимитов (зависит от тарифа)',
        'openai_description_5': 'Использует GPT-5 mini (быстрая и недорогая)',
        'openai_description_6': 'Платный (Input: $0.250, Output: $2.000 за 1M токенов)',
        'openai_description_7': 'Рекомендуется для: профессиональных проектов, баланс цена/качество',
        
        # Описания режимов обработки
        'prompt_same_note': 'ВАЖНО: Промпт одинаковый для обоих режимов!',
        'prompt_difference_note': 'Разница только в количестве обрабатываемых изображений.',
        'bulk_mode_title': 'bulk - Массовая обработка (Dataset Creation Bulk Gemini)',
        'bulk_mode_1': 'Обрабатывает: МНОГО изображений из Sample Dataset (до лимита)',
        'bulk_mode_2': 'Метод: listAllFilesSubfoldersInFolder с limit=10',
        'bulk_mode_3': 'Промпт: одинаковый для всех изображений',
        'bulk_mode_4': 'Обрабатывает весь датасет за один запуск',
        'bulk_mode_5': 'Эффективно для массовой обработки',
        'bulk_mode_6': 'Рекомендуется для: обработки всего датасета, массовой генерации',
        'detailed_mode_title': 'detailed - Обработка одного изображения (Dataset Image Generation NanoBanana)',
        'detailed_mode_1': 'Обрабатывает: ОДНО конкретное изображение из Sample Dataset',
        'detailed_mode_2': 'Метод: getFile для одного файла (выбор изображения)',
        'detailed_mode_3': 'Промпт: одинаковый (тот же что и для bulk)',
        'detailed_mode_4': 'Интерактивный выбор конкретного изображения из списка',
        'detailed_mode_5': 'Удобно для тестирования или обработки одного файла',
        'detailed_mode_6': 'Рекомендуется для: тестирования, обработки одного конкретного изображения',
        
        # Описания Wavespeed
        'wavespeed_description_1': 'Специализированные модели для конкретных задач',
        'wavespeed_description_2': 'Оптимизированные для Seedream и других моделей',
        'wavespeed_description_3': 'Конкурентные цены',
        'wavespeed_description_4': 'Поддержка 4K разрешения',
        'wavespeed_description_5': 'Хорошая документация API',
        'wavespeed_description_6': 'Рекомендуется для: специализированных задач, работы с Seedream',
        
        # Описания моделей Wavespeed
        'image_to_image': 'Image-to-Image (генерация и редактирование изображений):',
        'nano_banana_1': 'Редактирование изображений через текстовые инструкции',
        'nano_banana_2': 'Нативное 4K разрешение',
        'nano_banana_3': 'Многоязычный текст на изображениях',
        'nano_banana_4': 'Контроль камеры (угол, фокус, глубина резкости)',
        'nano_banana_5': 'Цена: $0.14 (1k/2k), $0.24 (4k)',
        'nano_banana_6': 'Идеально для: редактирования существующих изображений',
        'seedream_v45_1': 'Оптимизирована для типографики и постеров',
        'seedream_v45_2': 'Четкий рендеринг текста',
        'seedream_v45_3': 'Сильное следование промпту',
        'seedream_v45_4': 'Поддерживает image-to-image с референсными изображениями',
        'seedream_v45_5': 'Разрешение: 2560×1440 до 4096×4096',
        'seedream_v45_6': 'Цена: $0.04 за изображение (любое разрешение)',
        'seedream_v45_7': 'Идеально для: постеров, баннеров, брендовых визуалов',
        'seedream_v4_1': 'Предыдущее поколение Seedream',
        'seedream_v4_2': 'Высокое разрешение до 4K',
        'seedream_v4_3': 'Разнообразные стили иллюстраций',
        'seedream_v4_4': 'Поддерживает image-to-image с референсными изображениями',
        'seedream_v4_5': 'Seedream 4.5 улучшает рендеринг текста',
        'seedream_v4_6': 'Цена: $0.027 за изображение (любое разрешение)',
        'seedream_v4_7': 'Идеально для: иллюстраций и разнообразных стилей',
        'image_to_video': 'Image-to-Video (генерация видео из изображений):',
        'wan_25_1': 'Генерация видео из статичных изображений',
        'wan_25_2': 'Поддержка фонового аудио',
        'wan_25_3': 'Высокое качество видео',
        'kling_v26_1': 'Продвинутая модель для генерации видео',
        'kling_v26_2': 'Высокое качество и плавность',
        'kling_v26_3': 'Кинематографическая глубина',
        'kling_v26_4': 'Идеально для: профессиональных видео',
        'kling_v25_1': 'Быстрая версия модели Kling',
        'kling_v25_2': 'Плавное движение и стабильность',
        'kling_v25_3': 'Отличное следование промпту',
        'kling_v25_4': 'Идеально для: быстрой генерации видео',
        
        # Описания разрешений
        'resolution_1k_1': 'Быстрая генерация',
        'resolution_1k_2': 'Достаточно для большинства задач',
        'resolution_1k_3': 'Меньше деталей чем в 4K',
        'resolution_1k_4': 'Рекомендуется для: тестирования, быстрой обработки',
        'resolution_2k_1': 'Баланс между качеством и скоростью',
        'resolution_2k_2': 'Хорошая детализация',
        'resolution_2k_3': 'Рекомендуется для: большинства проектов',
        'resolution_4k_1': 'Максимальное качество и детализация',
        'resolution_4k_2': 'Идеально для печати и профессионального использования',
        'resolution_4k_3': 'Дольше генерация',
        'resolution_4k_4': 'Рекомендуется для: финальных результатов, печати',
        
        # Описания генерации captions
        'caption_generation_desc': 'Генерация подписей создаст .txt файлы для каждого сгенерированного изображения, которые можно использовать для обучения LoRA модели.',
        'caption_generation_yes': 'Да, генерировать подписи',
        'caption_generation_no': 'Нет, пропустить',
        'caption_yes_1': 'Создаст подписи для всех сгенерированных изображений',
        'caption_yes_2': 'Автоматически создаст zip архив с подписями',
        'caption_yes_3': 'Использует OpenAI для анализа изображений',
        'caption_yes_4': 'Требует OpenAI API ключ',
        'caption_yes_5': 'Дополнительные затраты на API',
        'caption_yes_6': 'Рекомендуется для: подготовки датасета для LoRA обучения',
        'caption_no_1': 'Быстрее обработка',
        'caption_no_2': 'Экономия на API',
        'caption_no_3': 'Рекомендуется для: если не планируете обучение LoRA',
        'caption_enabled': 'Генерация подписей включена',
        'caption_disabled': 'Генерация подписей отключена',
        
        # Описания trigger name
        'trigger_name_desc': 'Trigger name - это имя персонажа, которое будет использоваться в подписях.',
        'trigger_name_examples': "Примеры: 'Elara', 'John', 'CharacterName'",
        'trigger_name_warning': 'Важно: используйте одно слово или имя без пробелов',
        'trigger_name_set': 'Trigger name установлен: {name}',
        'trigger_name_not_set': 'Trigger name не указан! Генерация подписей будет пропущена.',
        'trigger_name_warning_caption': 'Внимание: генерация подписей включена, но trigger name не указан!',
        
        # Описания моделей OpenAI для captions
        'gpt51_caption_1': 'Лучшая модель для сложных задач',
        'gpt51_caption_2': 'Input: $1.250 / 1M tokens',
        'gpt51_caption_3': 'Output: $10.000 / 1M tokens',
        'gpt51_caption_4': 'Поддерживает анализ изображений (vision)',
        'gpt51_caption_5': 'Идеально для: максимального качества captions',
        'gpt4o_caption_1': 'Проверенная модель с поддержкой vision',
        'gpt4o_caption_2': 'Input: $2.50 / 1M tokens',
        'gpt4o_caption_3': 'Output: $10.00 / 1M tokens',
        'gpt4o_caption_4': 'Хорошее качество captions',
        'gpt4o_caption_5': 'Идеально для: совместимости и надежности',
        'caption_models_note': 'Примечание: GPT-5 Nano и GPT-5 Mini не поддерживают анализ изображений и не могут использоваться для генерации captions.',
        
        # Общие сообщения
        'please_select_1_or_2': 'Пожалуйста, выберите 1 или 2',
        'please_select_1': 'Пожалуйста, выберите 1',
        'must_select': 'обязательно',
    },
    'en': {
        # General
        'app_name': 'Dataset Creation - LoRA Dataset Creation',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Info',
        'yes': 'Yes',
        'no': 'No',
        'skip': 'Skip',
        'continue': 'Continue',
        'cancel': 'Cancel',
        'save': 'Save',
        'load': 'Load',
        'delete': 'Delete',
        'back': 'Back',
        'next': 'Next',
        'finish': 'Finish',
        'select': 'Select',
        'enter': 'Enter',
        'or': 'or',
        
        # Files and folders
        'file_not_found': 'File not found',
        'folder_not_found': 'Folder not found',
        'file_saved': 'File saved',
        'folder_created': 'Folder created',
        'file_exists': 'File already exists',
        
        # API and providers
        'api_key_missing': 'API key not set',
        'api_key_invalid': 'API key invalid',
        'provider_not_available': 'Provider not available',
        'request_failed': 'Request failed',
        'rate_limit_exceeded': 'Rate limit exceeded',
        
        # Generation
        'generating_prompt': 'Generating prompt...',
        'generating_image': 'Generating image...',
        'generating_caption': 'Generating caption...',
        'processing': 'Processing',
        'completed': 'Completed',
        'failed': 'Failed',
        
        # Menu
        'interactive_menu_title': 'Dataset Creation - Interactive Setup',
        'select_option': 'Select option',
        'select_settings': 'Select settings (Enter to skip, default values will be used):',
        'current_value': 'Current value',
        'not_selected': 'not selected',
        'your_choice': 'Your choice',
        'press_enter_to_skip': 'Press Enter to skip',
        'invalid_choice': 'Invalid choice',
        'selected': 'Selected',
        'using_value': 'Using value',
        'settings_selected': 'Settings selected!',
        'final_settings': 'Final settings:',
        'processing_mode': 'Processing mode',
        'image_generation_provider': 'Image/Video generation provider',
        'wavespeed_model': 'Wavespeed model',
        'resolution': 'Resolution for Wavespeed',
        'caption_generation': 'Caption generation for LoRA training',
        'trigger_name_prompt': 'Character name (trigger name) for LoRA',
        'openai_caption_model': 'OpenAI model for caption generation',
        
        # Settings
        'ai_provider': 'AI provider for prompt generation',
        'image_provider': 'Image generation provider',
        'prompt_template': 'Prompt template',
        'model': 'Model',
        'resolution': 'Resolution',
        'output_format': 'Output format',
        'trigger_name': 'Trigger name',
        'generate_captions': 'Generate captions',
        
        # Providers
        'gemini': 'Gemini',
        'openai': 'OpenAI',
        'wavespeed': 'Wavespeed',
        
        # Templates
        'bulk': 'Bulk (batch processing)',
        'detailed': 'Detailed (detailed processing)',
        
        # Profiles
        'profile': 'Profile',
        'profile_management': 'Profile Management',
        'profile_name': 'Profile name',
        'save_profile': 'Save settings as profile',
        'load_profile': 'Load profile',
        'profile_saved': 'Profile saved',
        'profile_loaded': 'Profile loaded',
        'profile_not_found': 'Profile not found',
        'profile_exists': 'Profile already exists',
        'found_profiles': 'Found {count} saved profiles:',
        'create_new_profile': 'Create new profile',
        'skip_use_temporary': 'Skip (use temporary settings)',
        'no_profiles_saved': 'No saved profiles.',
        'selected_profile': 'Selected profile: {name}',
        'invalid_choice_create_new': 'Invalid choice, creating new profile',
        'save_profile_title': 'Save Profile',
        'want_to_save_profile': 'Do you want to save these settings as a profile?',
        'yes_save': 'Yes, save',
        'no_skip': 'No, skip',
        'profile_already_exists': "Profile '{name}' already exists!",
        'overwrite_existing': 'Overwrite existing profile',
        'cancel_saving': 'Cancel saving',
        'saving_cancelled': 'Saving cancelled',
        'enter_profile_description': 'Enter profile description (optional, Enter to skip):',
        'profile_description_example': 'Example: {example}',
        'profile_created': "Profile '{name}' created!",
        'profile_updated': "Profile '{name}' updated!",
        'profile_path': 'Path: {path}',
        'error_saving_profile': 'Error saving profile: {error}',
        'settings_not_saved': 'Settings not saved (will be used only for this run)',
        
        # Results
        'images_processed': 'Images processed',
        'images_generated': 'Images generated',
        'captions_generated': 'Captions generated',
        'zip_created': 'Zip archive created',
        'output_folder': 'Output folder',
        
        # Processing
        'loading_ref_images': 'Loading reference images...',
        'found_ref_images': 'Found {count} reference images',
        'loading_sample_images': 'Loading sample images...',
        'mode_detailed': 'Mode: detailed (single image processing)',
        'mode_detailed_corresponds': 'Corresponds to: Dataset Image Generation NanoBanana 2 (getFile for one file)',
        'mode_bulk': 'Mode: bulk (batch processing up to {limit} images)',
        'mode_bulk_corresponds': 'Corresponds to: Dataset Creation Bulk Gemini (listAllFiles with limit={limit})',
        'found_sample_images': 'Found {count} sample images',
        'found_sample_images_for_processing': 'Found {count} sample images for processing',
        'image_not_selected': 'Image not selected, processing cancelled',
        'image_selected': 'Selected image: {name}',
        'processing_image': 'Processing {current}/{total}: {name}',
        'generating_prompt': 'Generating prompt...',
        'prompt_generated': 'Prompt generated ({length} characters)',
        'generating_image': 'Generating image via {provider} ({model})...',
        'image_saved': 'Image saved: {path}',
        'video_saved': 'Video saved: {path}',
        'generating_captions': 'Generating captions for LoRA training...',
        'generating_caption_for': 'Generating caption for {name}...',
        'caption_saved': 'Caption saved: {name}',
        'creating_zip': 'Creating zip archive: {name}...',
        'zip_created_path': 'Zip archive created: {path}',
        'total_files': 'Total files: {images} images + {captions} captions',
        'all_files_saved_in': 'All files saved in: {path}',
        'processing_completed': 'Processing completed! Results saved in: {path}',
        'caption_generation_skipped': 'Caption generation will be skipped',
        'caption_generator_not_initialized': 'Caption generator not initialized',
        'error_generating_caption_for': 'Error generating caption for {name}: {error}',
        
        # Wavespeed errors
        'wavespeed_timeout_error': 'Timeout when requesting Wavespeed API (timeout: {timeout} seconds). Server did not respond in time. Please try again later or reduce image size.',
        'wavespeed_request_error': 'Error requesting Wavespeed: {error}',
        'wavespeed_api_error': 'Wavespeed API returned error: {error}',
        'server_response': 'Server response',
        'unknown_error': 'Unknown error',
        
        # Image selection
        'image_selection_title': 'Select image from Sample Dataset',
        'image_selection_available': 'Available images',
        
        # Errors
        'error_loading_config': 'Error loading configuration',
        'error_saving_config': 'Error saving configuration',
        'error_processing_image': 'Error processing image',
        'error_generating_prompt': 'Error generating prompt',
        'error_generating_image': 'Error generating image',
        'error_generating_caption': 'Error generating caption',
        
        # Testing
        'testing_models': 'Testing models',
        'testing_captions': 'Testing caption generation',
        'test_successful': 'Test successful',
        'test_failed': 'Test failed',
        
        # Info
        'select_language': 'Select language / Выберите язык',
        'language_set': 'Language set',
        
        # Описания AI провайдеров
        'gemini_description_1': 'Fast prompt generation',
        'gemini_description_2': 'Free with limits (60 requests/min)',
        'gemini_description_3': 'Good image analysis quality',
        'gemini_description_4': 'Multimodal request support',
        'gemini_description_5': 'Has request limits',
        'gemini_description_6': 'Recommended for: getting started, testing, saving money',
        'openai_description_1': 'High analysis accuracy',
        'openai_description_2': 'Better context understanding',
        'openai_description_3': 'More structured responses',
        'openai_description_4': 'No hard limits (depends on plan)',
        'openai_description_5': 'Uses GPT-5 mini (fast and affordable)',
        'openai_description_6': 'Paid (Input: $0.250, Output: $2.000 per 1M tokens)',
        'openai_description_7': 'Recommended for: professional projects, price/quality balance',
        
        # Описания режимов обработки
        'prompt_same_note': 'IMPORTANT: Prompt is the same for both modes!',
        'prompt_difference_note': 'Difference is only in the number of images processed.',
        'bulk_mode_title': 'bulk - Batch processing (Dataset Creation Bulk Gemini)',
        'bulk_mode_1': 'Processes: MANY images from Sample Dataset (up to limit)',
        'bulk_mode_2': 'Method: listAllFilesSubfoldersInFolder with limit=10',
        'bulk_mode_3': 'Prompt: same for all images',
        'bulk_mode_4': 'Processes entire dataset in one run',
        'bulk_mode_5': 'Efficient for batch processing',
        'bulk_mode_6': 'Recommended for: processing entire dataset, batch generation',
        'detailed_mode_title': 'detailed - Single image processing (Dataset Image Generation NanoBanana)',
        'detailed_mode_1': 'Processes: ONE specific image from Sample Dataset',
        'detailed_mode_2': 'Method: getFile for one file (image selection)',
        'detailed_mode_3': 'Prompt: same (same as for bulk)',
        'detailed_mode_4': 'Interactive selection of specific image from list',
        'detailed_mode_5': 'Convenient for testing or processing one file',
        'detailed_mode_6': 'Recommended for: testing, processing one specific image',
        
        # Описания Wavespeed
        'wavespeed_description_1': 'Specialized models for specific tasks',
        'wavespeed_description_2': 'Optimized for Seedream and other models',
        'wavespeed_description_3': 'Competitive prices',
        'wavespeed_description_4': '4K resolution support',
        'wavespeed_description_5': 'Good API documentation',
        'wavespeed_description_6': 'Recommended for: specialized tasks, working with Seedream',
        
        # Описания моделей Wavespeed
        'image_to_image': 'Image-to-Image (generation and editing):',
        'nano_banana_1': 'Image editing through text instructions',
        'nano_banana_2': 'Native 4K resolution',
        'nano_banana_3': 'Multilingual text on images',
        'nano_banana_4': 'Camera control (angle, focus, depth of field)',
        'nano_banana_5': 'Price: $0.14 (1k/2k), $0.24 (4k)',
        'nano_banana_6': 'Ideal for: editing existing images',
        'seedream_v45_1': 'Optimized for typography and posters',
        'seedream_v45_2': 'Clear text rendering',
        'seedream_v45_3': 'Strong prompt following',
        'seedream_v45_4': 'Supports image-to-image with reference images',
        'seedream_v45_5': 'Resolution: 2560×1440 to 4096×4096',
        'seedream_v45_6': 'Price: $0.04 per image (any resolution)',
        'seedream_v45_7': 'Ideal for: posters, banners, brand visuals',
        'seedream_v4_1': 'Previous generation Seedream',
        'seedream_v4_2': 'High resolution up to 4K',
        'seedream_v4_3': 'Various illustration styles',
        'seedream_v4_4': 'Supports image-to-image with reference images',
        'seedream_v4_5': 'Seedream 4.5 improves text rendering',
        'seedream_v4_6': 'Price: $0.027 per image (any resolution)',
        'seedream_v4_7': 'Ideal for: illustrations and various styles',
        'image_to_video': 'Image-to-Video (video generation from images):',
        'wan_25_1': 'Video generation from static images',
        'wan_25_2': 'Background audio support',
        'wan_25_3': 'High quality video',
        'kling_v26_1': 'Advanced model for video generation',
        'kling_v26_2': 'High quality and smoothness',
        'kling_v26_3': 'Cinematic depth',
        'kling_v26_4': 'Ideal for: professional videos',
        'kling_v25_1': 'Fast version of Kling model',
        'kling_v25_2': 'Smooth movement and stability',
        'kling_v25_3': 'Excellent prompt following',
        'kling_v25_4': 'Ideal for: fast video generation',
        
        # Описания разрешений
        'resolution_1k_1': 'Fast generation',
        'resolution_1k_2': 'Sufficient for most tasks',
        'resolution_1k_3': 'Less detail than 4K',
        'resolution_1k_4': 'Recommended for: testing, fast processing',
        'resolution_2k_1': 'Balance between quality and speed',
        'resolution_2k_2': 'Good detail',
        'resolution_2k_3': 'Recommended for: most projects',
        'resolution_4k_1': 'Maximum quality and detail',
        'resolution_4k_2': 'Ideal for printing and professional use',
        'resolution_4k_3': 'Longer generation time',
        'resolution_4k_4': 'Recommended for: final results, printing',
        
        # Описания генерации captions
        'caption_generation_desc': 'Caption generation will create .txt files for each generated image that can be used for LoRA model training.',
        'caption_generation_yes': 'Yes, generate captions',
        'caption_generation_no': 'No, skip',
        'caption_yes_1': 'Will create captions for all generated images',
        'caption_yes_2': 'Will automatically create zip archive with captions',
        'caption_yes_3': 'Uses OpenAI for image analysis',
        'caption_yes_4': 'Requires OpenAI API key',
        'caption_yes_5': 'Additional API costs',
        'caption_yes_6': 'Recommended for: preparing dataset for LoRA training',
        'caption_no_1': 'Faster processing',
        'caption_no_2': 'API cost savings',
        'caption_no_3': 'Recommended for: if you don\'t plan LoRA training',
        'caption_enabled': 'Caption generation enabled',
        'caption_disabled': 'Caption generation disabled',
        
        # Описания trigger name
        'trigger_name_desc': 'Trigger name is the character name that will be used in captions.',
        'trigger_name_examples': "Examples: 'Elara', 'John', 'CharacterName'",
        'trigger_name_warning': 'Important: use one word or name without spaces',
        'trigger_name_set': 'Trigger name set: {name}',
        'trigger_name_not_set': 'Trigger name not specified! Caption generation will be skipped.',
        'trigger_name_warning_caption': 'Warning: caption generation enabled, but trigger name not specified!',
        
        # Описания моделей OpenAI для captions
        'gpt51_caption_1': 'Best model for complex tasks',
        'gpt51_caption_2': 'Input: $1.250 / 1M tokens',
        'gpt51_caption_3': 'Output: $10.000 / 1M tokens',
        'gpt51_caption_4': 'Supports image analysis (vision)',
        'gpt51_caption_5': 'Ideal for: maximum caption quality',
        'gpt4o_caption_1': 'Proven model with vision support',
        'gpt4o_caption_2': 'Input: $2.50 / 1M tokens',
        'gpt4o_caption_3': 'Output: $10.00 / 1M tokens',
        'gpt4o_caption_4': 'Good caption quality',
        'gpt4o_caption_5': 'Ideal for: compatibility and reliability',
        'caption_models_note': 'Note: GPT-5 Nano and GPT-5 Mini do not support image analysis and cannot be used for caption generation.',
        
        # Общие сообщения
        'please_select_1_or_2': 'Please select 1 or 2',
        'please_select_1': 'Please select 1',
        'must_select': 'required',
    }
}


class I18n:
    """Класс для работы с локализацией"""
    
    def __init__(self, language: Optional[str] = None):
        """
        Инициализация локализации
        
        Args:
            language: Код языка ('ru' или 'en'). Если None, определяется автоматически
        """
        self.language = self._detect_language(language)
        self.translations = TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANGUAGE])
    
    def _detect_language(self, language: Optional[str] = None) -> str:
        """Определяет язык из переменной окружения или параметра"""
        if language:
            if language.lower() in SUPPORTED_LANGUAGES:
                return language.lower()
        
        # Пытаемся загрузить из config.json
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    lang = config.get('language', '').lower()
                    if lang in SUPPORTED_LANGUAGES:
                        return lang
        except:
            pass
        
        # Пытаемся определить из переменной окружения
        env_lang = os.getenv('LANG', '').lower()
        if 'ru' in env_lang:
            return 'ru'
        elif 'en' in env_lang:
            return 'en'
        
        # По умолчанию
        return DEFAULT_LANGUAGE
    
    def t(self, key: str, **kwargs) -> str:
        """
        Получить переведенный текст
        
        Args:
            key: Ключ перевода
            **kwargs: Параметры для форматирования строки
        
        Returns:
            Переведенный текст или ключ, если перевод не найден
        """
        text = self.translations.get(key, key)
        
        # Если есть параметры для форматирования
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        
        return text
    
    def set_language(self, language: str):
        """Установить язык"""
        if language.lower() in SUPPORTED_LANGUAGES:
            self.language = language.lower()
            self.translations = TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANGUAGE])
            return True
        return False
    
    def get_language(self) -> str:
        """Получить текущий язык"""
        return self.language
    
    def get_supported_languages(self) -> list:
        """Получить список поддерживаемых языков"""
        return SUPPORTED_LANGUAGES.copy()


# Глобальный экземпляр локализации
_i18n_instance: Optional[I18n] = None


def get_i18n(language: Optional[str] = None) -> I18n:
    """
    Получить экземпляр локализации (singleton)
    
    Args:
        language: Код языка для инициализации (только при первом вызове)
    
    Returns:
        Экземпляр I18n
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(language)
    return _i18n_instance


def set_language(language: str) -> bool:
    """
    Установить язык для глобального экземпляра
    
    Args:
        language: Код языка ('ru' или 'en')
    
    Returns:
        True если язык установлен, False если язык не поддерживается
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(language)
    else:
        return _i18n_instance.set_language(language)
    return True


# Удобная функция для быстрого доступа к переводам
def _(key: str, **kwargs) -> str:
    """
    Получить переведенный текст (удобная функция)
    
    Args:
        key: Ключ перевода
        **kwargs: Параметры для форматирования
    
    Returns:
        Переведенный текст
    """
    return get_i18n().t(key, **kwargs)

