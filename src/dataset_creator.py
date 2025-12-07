"""Основной класс для создания датасета"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    from i18n import get_i18n
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    def get_i18n():
        class SimpleI18n:
            def t(self, key, **kwargs):
                return key
        return SimpleI18n()

from .config import Config
from .file_manager import LocalFileManager
from .prompt_generator import PromptGenerator
from .image_generator import ImageGenerator
from .caption_generator import CaptionGenerator


class DatasetCreator:
    """Основной класс для создания датасета"""
    
    def __init__(self, config: Config):
        self.config = config
        self.file_manager = LocalFileManager()
        self.prompt_generator = PromptGenerator(config)
        self.image_generator = ImageGenerator(config)
        
        # Инициализируем генератор подписей только если нужно
        self.caption_generator = None
        if self.config.generate_captions and self.config.trigger_name:
            try:
                self.caption_generator = CaptionGenerator(config)
            except Exception as e:
                i18n = get_i18n()
                print(f"   ⚠️  {i18n.t('caption_generation_skipped_error', error=e)}")
                print(f"   {i18n.t('caption_generation_skipped')}")
        
        # Создаем выходную папку
        Path(self.config.output_folder).mkdir(parents=True, exist_ok=True)
        
        # Список сгенерированных изображений для создания captions
        self.generated_images = []
    
    def _get_unique_file_path(self, base_path: str) -> str:
        """Генерирует уникальное имя файла, добавляя timestamp если файл уже существует"""
        path = Path(base_path)
        output_dir = path.parent
        stem = path.stem
        suffix = path.suffix
        
        # Если файл не существует, возвращаем исходный путь
        if not path.exists():
            return str(path)
        
        # Если файл существует, добавляем timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_path = output_dir / f"{stem}_{timestamp}{suffix}"
        
        # Если и с timestamp файл существует (маловероятно, но на всякий случай), добавляем счетчик
        counter = 1
        while unique_path.exists():
            unique_path = output_dir / f"{stem}_{timestamp}_{counter}{suffix}"
            counter += 1
        
        return str(unique_path)
    
    def process_dataset(self):
        """Обрабатывает весь датасет"""
        i18n = get_i18n()
        print(f"📁 {i18n.t('loading_ref_images')}")
        ref_files = self.file_manager.list_image_files(
            self.config.influencer_ref_folder,
            self.config.limit_ref_images
        )
        print(f"   {i18n.t('found_ref_images', count=len(ref_files))}")
        
        print(f"📁 {i18n.t('loading_sample_images')}")
        # Логика зависит от шаблона промпта (соответствует оригинальным Make.com workflow):
        # - bulk: использует listAllFilesSubfoldersInFolder с limit=10 → обрабатывает МНОГО изображений
        # - detailed: использует getFile с конкретным файлом → обрабатывает ОДНО изображение
        if self.config.prompt_template == 'detailed':
            # Для detailed загружаем все изображения для выбора
            limit = self.config.limit_sample_images
            print(f"   {i18n.t('mode_detailed')}")
            print(f"   {i18n.t('mode_detailed_corresponds')}")
            
            # Проверяем наличие файлов в подпапках
            sample_folder = Path(self.config.sample_dataset_folder)
            normal_folder = sample_folder / 'normal'
            
            if normal_folder.exists() and normal_folder.is_dir():
                normal_files = list(normal_folder.glob('*.{jpg,jpeg,png,gif,bmp,webp}'))
                normal_files = [f for f in normal_files if f.is_file()]
                if len(normal_files) == 0:
                    print(f"   ℹ️  {i18n.t('folder_normal_empty')}")
            
            if self.config.nsfw_enabled:
                nsfw_folder = sample_folder / 'nsfw'
                if nsfw_folder.exists() and nsfw_folder.is_dir():
                    nsfw_files = list(nsfw_folder.glob('*.{jpg,jpeg,png,gif,bmp,webp}'))
                    nsfw_files = [f for f in nsfw_files if f.is_file()]
                    if len(nsfw_files) == 0:
                        print(f"   ℹ️  {i18n.t('folder_nsfw_empty')}")
            
            # Загружаем все доступные изображения для выбора
            all_sample_files = self.file_manager.list_image_files(
                self.config.sample_dataset_folder,
                limit,
                include_nsfw=self.config.nsfw_enabled
            )
            print(f"   {i18n.t('found_sample_images', count=len(all_sample_files))}")
            
            # Интерактивный выбор изображения
            selected_file = self._select_sample_image(all_sample_files)
            if not selected_file:
                print(f"   ⚠️  {i18n.t('image_not_selected')}")
                return
            
            sample_files = [selected_file]
            print(f"   ✓ {i18n.t('image_selected', name=selected_file['name'])}")
        else:
            # Для bulk обрабатываем все изображения до лимита (как в оригинальном workflow)
            limit = self.config.limit_sample_images
            print(f"   {i18n.t('mode_bulk', limit=limit)}")
            print(f"   {i18n.t('mode_bulk_corresponds', limit=limit)}")
            
            # Проверяем наличие файлов в подпапках
            sample_folder = Path(self.config.sample_dataset_folder)
            normal_folder = sample_folder / 'normal'
            
            if normal_folder.exists() and normal_folder.is_dir():
                normal_files = list(normal_folder.glob('*.{jpg,jpeg,png,gif,bmp,webp}'))
                normal_files = [f for f in normal_files if f.is_file()]
                if len(normal_files) == 0:
                    print(f"   ℹ️  {i18n.t('folder_normal_empty')}")
            
            if self.config.nsfw_enabled:
                nsfw_folder = sample_folder / 'nsfw'
                if nsfw_folder.exists() and nsfw_folder.is_dir():
                    nsfw_files = list(nsfw_folder.glob('*.{jpg,jpeg,png,gif,bmp,webp}'))
                    nsfw_files = [f for f in nsfw_files if f.is_file()]
                    if len(nsfw_files) == 0:
                        print(f"   ℹ️  {i18n.t('folder_nsfw_empty')}")
            
            sample_files = self.file_manager.list_image_files(
                self.config.sample_dataset_folder,
                limit,
                include_nsfw=self.config.nsfw_enabled
            )
            print(f"   {i18n.t('found_sample_images_for_processing', count=len(sample_files))}")
        
        # Загружаем референсные изображения
        ref_images_data = []
        for ref_file in ref_files[:2]:  # Берем первые 2
            data, _ = self.file_manager.read_file(ref_file['path'])
            ref_images_data.append(data)
            print(f"   ✓ {ref_file['name']}")
        
        # Обрабатываем каждое sample изображение
        for idx, sample_file in enumerate(sample_files, 1):
            print(f"\n🖼️  {i18n.t('processing_image', current=idx, total=len(sample_files), name=sample_file['name'])}")
            
            try:
                # Определяем тип контента по пути файла
                content_type = sample_file.get('content_type')
                if not content_type:
                    # Определяем по пути
                    file_path = sample_file.get('path', '')
                    if 'nsfw' in file_path.lower():
                        content_type = 'nsfw'
                    elif 'normal' in file_path.lower():
                        content_type = 'normal'
                
                # Если NSFW отключен, пропускаем NSFW файлы
                if content_type == 'nsfw' and not self.config.nsfw_enabled:
                    print(f"   ⏭️  {i18n.t('skipped_nsfw_disabled')}")
                    continue
                
                # Сохраняем текущие настройки
                original_ai_provider = self.config.ai_provider
                original_gemini_model = self.config.gemini_model
                original_openai_model = self.config.openai_model
                original_grok_model = self.config.grok_model
                original_wavespeed_model = self.config.wavespeed_model
                original_caption_provider = self.config.caption_provider
                original_openai_caption_model = self.config.openai_caption_model
                original_grok_caption_model = self.config.grok_caption_model
                
                # Применяем настройки для типа контента
                settings_applied = False
                if content_type == 'nsfw':
                    if self.config.ai_provider_nsfw:
                        self.config.ai_provider = self.config.ai_provider_nsfw
                        if self.config.ai_provider_nsfw == 'gemini':
                            self.config.gemini_model = self.config.gemini_model_nsfw
                        elif self.config.ai_provider_nsfw == 'openai':
                            self.config.openai_model = self.config.openai_model_nsfw
                        elif self.config.ai_provider_nsfw == 'grok':
                            self.config.grok_model = self.config.grok_model_nsfw
                        settings_applied = True
                    if self.config.wavespeed_model_nsfw:
                        self.config.wavespeed_model = self.config.wavespeed_model_nsfw
                        settings_applied = True
                    if self.config.caption_provider_nsfw:
                        self.config.caption_provider = self.config.caption_provider_nsfw
                        if self.config.caption_provider_nsfw == 'openai':
                            self.config.openai_caption_model = self.config.openai_caption_model_nsfw
                        elif self.config.caption_provider_nsfw == 'grok':
                            self.config.grok_caption_model = self.config.grok_caption_model_nsfw
                        settings_applied = True
                    if settings_applied:
                        print(f"   📌 {i18n.t('using_nsfw_settings')}")
                    else:
                        print(f"   📌 {i18n.t('using_main_settings_nsfw_not_set')}")
                elif content_type == 'normal':
                    if self.config.ai_provider_normal:
                        self.config.ai_provider = self.config.ai_provider_normal
                        if self.config.ai_provider_normal == 'gemini':
                            self.config.gemini_model = self.config.gemini_model_normal
                        elif self.config.ai_provider_normal == 'openai':
                            self.config.openai_model = self.config.openai_model_normal
                        elif self.config.ai_provider_normal == 'grok':
                            self.config.grok_model = self.config.grok_model_normal
                        settings_applied = True
                    if self.config.wavespeed_model_normal:
                        self.config.wavespeed_model = self.config.wavespeed_model_normal
                        settings_applied = True
                    if self.config.caption_provider_normal:
                        self.config.caption_provider = self.config.caption_provider_normal
                        if self.config.caption_provider_normal == 'openai':
                            self.config.openai_caption_model = self.config.openai_caption_model_normal
                        elif self.config.caption_provider_normal == 'grok':
                            self.config.grok_caption_model = self.config.grok_caption_model_normal
                        settings_applied = True
                    if settings_applied:
                        print(f"   📌 {i18n.t('using_normal_settings')}")
                    else:
                        print(f"   📌 {i18n.t('using_main_settings_normal_not_set')}")
                else:
                    # Если content_type не определен, используем основные настройки
                    print(f"   📌 {i18n.t('using_main_settings')}")
                
                # Обновляем генераторы с новыми настройками
                self.prompt_generator.config = self.config
                self.prompt_generator.setup_provider()  # Переинициализируем провайдер
                self.image_generator.config = self.config
                if self.caption_generator:
                    self.caption_generator.config = self.config
                    # Переинициализируем caption generator если провайдер изменился
                    try:
                        self.caption_generator = CaptionGenerator(self.config)
                    except Exception:
                        pass  # Оставляем старый если не удалось создать новый
                
                # Читаем sample изображение
                sample_data, sample_name = self.file_manager.read_file(sample_file['path'])
                
                # Генерируем промпт
                print(f"   🤖 {i18n.t('generating_prompt')}")
                prompt = self.prompt_generator.generate_prompt(ref_images_data, sample_data)
                print(f"   ✓ {i18n.t('prompt_generated', length=len(prompt))}")
                
                # Сохраняем промпт (с уникальным именем)
                base_prompt_path = os.path.join(
                    self.config.output_folder,
                    f"{Path(sample_name).stem}_prompt.txt"
                )
                prompt_path = self._get_unique_file_path(base_prompt_path)
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    f.write(prompt)
                
                # Определяем тип вывода (изображение или видео)
                is_video = False
                if self.config.image_provider == 'wavespeed':
                    is_video = ('image-to-video' in self.config.wavespeed_model or 
                               '/video' in self.config.wavespeed_model or
                               'video' in self.config.wavespeed_model.lower())
                output_type = "видео" if is_video else "изображения"
                default_ext = "mp4" if is_video else "png"
                
                # Генерируем изображение/видео
                model_name = self.config.wavespeed_model
                print(f"   🎨 {i18n.t('generating_image', provider=self.config.image_provider, model=model_name)}")
                
                # Восстанавливаем оригинальные настройки
                self.config.ai_provider = original_ai_provider
                self.config.gemini_model = original_gemini_model
                self.config.openai_model = original_openai_model
                self.config.grok_model = original_grok_model
                self.config.wavespeed_model = original_wavespeed_model
                self.config.caption_provider = original_caption_provider
                self.config.openai_caption_model = original_openai_caption_model
                self.config.grok_caption_model = original_grok_caption_model
                
                # Определяем путь для сохранения
                if self.config.generate_captions and self.config.trigger_name and not is_video:
                    # Если включена генерация captions, используем формат trigger_name_0001.png
                    img_index = len(self.generated_images) + 1
                    lora_dir = Path(self.config.output_folder) / "lora_dataset"
                    lora_dir.mkdir(exist_ok=True)
                    output_path = lora_dir / f"{self.config.trigger_name}_{img_index:04d}.{default_ext}"
                else:
                    # Обычный формат с уникальным именем
                    base_output_path = os.path.join(
                        self.config.output_folder,
                        f"{Path(sample_name).stem}_generated.{default_ext}"
                    )
                    output_path = self._get_unique_file_path(base_output_path)
                
                self.image_generator.generate_image(
                    ref_images_data,
                    sample_data,
                    prompt,
                    str(output_path)
                )
                if is_video:
                    print(f"   ✓ {i18n.t('video_saved', path=output_path)}")
                else:
                    print(f"   ✓ {i18n.t('image_saved', path=output_path)}")
                
                # Сохраняем информацию о сгенерированном изображении для создания captions
                if not is_video:  # Captions только для изображений, не для видео
                    self.generated_images.append({
                        'path': str(output_path),
                        'original_name': sample_name,
                        'index': len(self.generated_images) + 1  # Индекс начинается с 1 для _0001, _0002 и т.д.
                    })
                
            except Exception as e:
                i18n = get_i18n()
                print(f"   ❌ {i18n.t('error_processing_image')}: {sample_file['name']}: {e}")
                continue
        
        # Генерируем captions если нужно
        if self.config.generate_captions and self.config.trigger_name and self.generated_images:
            print(f"\n📝 {i18n.t('generating_captions')}")
            self._generate_captions()
        
        print(f"\n✅ {i18n.t('processing_completed', path=self.config.output_folder)}")
    
    def _select_sample_image(self, sample_files: List[Dict]) -> Optional[Dict]:
        """Интерактивный выбор одного изображения из Sample Dataset"""
        if not sample_files:
            print("   ⚠️  Нет доступных изображений для выбора")
            return None
        
        print("\n" + "="*60)
        print("  🖼️  Выбор изображения из Sample Dataset")
        print("="*60)
        print("\nДоступные изображения:")
        
        for idx, file_info in enumerate(sample_files, 1):
            size_mb = file_info.get('size', 0) / (1024 * 1024)
            print(f"   [{idx}] {file_info['name']} ({size_mb:.2f} MB)")
        
        print(f"\n   [0] Отмена")
        
        while True:
            try:
                choice = input("\n   Выберите номер изображения (1-{} или 0 для отмены): ".format(len(sample_files))).strip()
                
                if choice == '0':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(sample_files):
                    return sample_files[choice_num - 1]
                else:
                    print(f"   ⚠️  Пожалуйста, выберите число от 1 до {len(sample_files)} или 0 для отмены")
            except ValueError:
                print(f"   ⚠️  Пожалуйста, введите число от 1 до {len(sample_files)} или 0 для отмены")
            except KeyboardInterrupt:
                print("\n   ⚠️  Выбор отменен")
                return None
    
    def _generate_captions(self):
        """Генерирует подписи для всех сгенерированных изображений и создает zip архив"""
        i18n = get_i18n()
        if not self.caption_generator:
            print(f"   ⚠️  {i18n.t('caption_generator_not_initialized')}")
            return
        
        trigger_name = self.config.trigger_name
        # Используем ту же папку, где сохранены изображения (lora_dataset)
        lora_dir = Path(self.config.output_folder) / "lora_dataset"
        lora_dir.mkdir(exist_ok=True)
        
        caption_files = []
        image_files = []
        
        for img_info in self.generated_images:
            img_path = Path(img_info['path'])
            img_index = img_info['index']
            
            try:
                print(f"   📝 {i18n.t('generating_caption_for', name=img_path.name)}")
                
                # Генерируем подпись
                caption = self.caption_generator.generate_caption(str(img_path), trigger_name)
                
                # Создаем имя файла: trigger_name_0001.txt, trigger_name_0002.txt и т.д.
                caption_filename = f"{trigger_name}_{img_index:04d}.txt"
                caption_path = lora_dir / caption_filename
                
                # Сохраняем подпись в ту же папку, где изображение
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(caption)
                
                caption_files.append({
                    'path': caption_path,
                    'filename': caption_filename
                })
                
                # Изображение уже должно быть в lora_dir с правильным именем (сохранено при генерации)
                # Проверяем, что имя соответствует формату trigger_name_XXXX.png
                expected_img_name = f"{trigger_name}_{img_index:04d}{img_path.suffix}"
                if img_path.parent != lora_dir or img_path.name != expected_img_name:
                    # Если изображение не в lora_dir или с неправильным именем, копируем/перемещаем его
                    new_img_path = lora_dir / expected_img_name
                    if img_path.exists():
                        shutil.copy2(img_path, new_img_path)
                        # Удаляем старое изображение если оно было в другой папке
                        if img_path.parent != lora_dir:
                            try:
                                img_path.unlink()
                            except:
                                pass
                    # Обновляем путь в информации об изображении
                    img_info['path'] = str(new_img_path)
                    image_files.append({
                        'path': new_img_path,
                        'filename': expected_img_name
                    })
                else:
                    # Изображение уже в правильной папке с правильным именем
                    image_files.append({
                        'path': img_path,
                        'filename': img_path.name
                    })
                
                print(f"   ✓ Подпись сохранена: {caption_filename}")
                
            except Exception as e:
                print(f"   ❌ {i18n.t('error_generating_caption_for', name=img_path.name, error=e)}")
                continue
        
        # Создаем zip архив со всеми файлами (изображения + подписи)
        if caption_files:
            zip_path = Path(self.config.output_folder) / f"{trigger_name}_lora_dataset.zip"
            i18n = get_i18n()
            print(f"\n   📦 {i18n.t('creating_zip', name=zip_path.name)}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Добавляем изображения
                for img_file in image_files:
                    zipf.write(img_file['path'], img_file['filename'])
                # Добавляем подписи
                for caption_file in caption_files:
                    zipf.write(caption_file['path'], caption_file['filename'])
            
            print(f"   ✓ {i18n.t('zip_created_path', path=zip_path)}")
            print(f"   📁 {i18n.t('total_files', images=len(image_files), captions=len(caption_files))}")
            print(f"   📂 {i18n.t('all_files_saved_in', path=lora_dir)}")

