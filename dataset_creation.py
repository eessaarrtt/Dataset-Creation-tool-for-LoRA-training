#!/usr/bin/env python3
"""
Dataset Creation Bulk - Python аналог Make.com workflow
Поддерживает локальное хранение, выбор между Gemini/OpenAI и Wavespeed
"""

import os
import json
import base64
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import mimetypes
import zipfile

# Импорт системы локализации
try:
    from i18n import get_i18n, set_language
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    # Простой fallback если i18n не доступен
    def get_i18n():
        class SimpleI18n:
            def t(self, key, **kwargs):
                return key
        return SimpleI18n()
    def set_language(lang):
        return True

# AI providers
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# HTTP requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Config:
    """Конфигурация приложения с поддержкой профилей"""
    
    PROFILES_DIR = "profiles"
    
    def __init__(self, config_file: Optional[str] = None, profile_name: Optional[str] = None):
        self.config_file = config_file or "config.json"
        self.profile_name = profile_name
        self.profiles_dir = Path(self.PROFILES_DIR)
        self.profiles_dir.mkdir(exist_ok=True)
        self.load_config()
    
    def load_config(self):
        """Загружает конфигурацию из файла или создает минимальную"""
        # Загружаем базовый config.json (пути к папкам и API ключи)
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
        else:
            base_config = self.get_minimal_config()
            self.save_base_config(base_config)
        
        # Пути к папкам (всегда из базового config.json)
        self.influencer_ref_folder = base_config.get('influencer_ref_folder', './Influencer Reference Images')
        self.sample_dataset_folder = base_config.get('sample_dataset_folder', './Sample Dataset')
        self.output_folder = base_config.get('output_folder', './output')
        
        # Лимиты (из базового config)
        self.limit_ref_images = base_config.get('limit_ref_images', 10)
        self.limit_sample_images = base_config.get('limit_sample_images', 10)
        
        # API ключи из config.json (используются по умолчанию)
        self.gemini_api_key = base_config.get('gemini_api_key', '')
        self.openai_api_key = base_config.get('openai_api_key', '')
        self.wavespeed_api_key = base_config.get('wavespeed_api_key', '')
        
        # Если указан профиль, загружаем его (переопределяет ключи если они там есть)
        if self.profile_name:
            self.load_from_profile(self.profile_name)
        else:
            # Иначе используем минимальные значения для выбора провайдеров/моделей
            self.set_minimal_defaults(base_config)
    
    def set_minimal_defaults(self, base_config: Dict):
        """Устанавливает минимальные значения по умолчанию (не заполненные)"""
        # AI провайдер для промптов
        self.ai_provider = None
        
        # Модели (ключи уже загружены из config.json)
        self.gemini_model = 'gemini-2.5-flash'
        self.openai_model = 'gpt-5-mini'
        
        # Image generation провайдер
        self.image_provider = None
        
        # Wavespeed настройки (ключ уже загружен из config.json)
        self.wavespeed_size = '2880*4096'
        self.wavespeed_model = ''
        self.wavespeed_resolution = '1k'
        self.wavespeed_output_format = 'png'
        
        # Промпт шаблон
        self.prompt_template = 'bulk'
        
        # LoRA captions настройки
        self.trigger_name = ''
        self.generate_captions = False
        self.openai_caption_model = 'gpt-5.1'  # Модель для генерации captions (gpt-5.1 или gpt-4o поддерживают vision)
    
    def load_from_profile(self, profile_name: str):
        """Загружает настройки из профиля"""
        profile_path = self.profiles_dir / f"{profile_name}.json"
        if not profile_path.exists():
            raise FileNotFoundError(f"Профиль '{profile_name}' не найден")
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        # Загружаем настройки из профиля
        # API ключи из профиля переопределяют ключи из config.json (если указаны)
        self.ai_provider = profile.get('ai_provider')
        if profile.get('gemini_api_key'):
            self.gemini_api_key = profile.get('gemini_api_key')
        self.gemini_model = profile.get('gemini_model', 'gemini-2.5-flash')
        if profile.get('openai_api_key'):
            self.openai_api_key = profile.get('openai_api_key')
        self.openai_model = profile.get('openai_model', 'gpt-5-mini')
        self.image_provider = profile.get('image_provider')
        if profile.get('wavespeed_api_key'):
            self.wavespeed_api_key = profile.get('wavespeed_api_key')
        self.wavespeed_size = profile.get('wavespeed_size', '2880*4096')
        self.wavespeed_model = profile.get('wavespeed_model', '')
        self.wavespeed_resolution = profile.get('wavespeed_resolution', '1k')
        self.wavespeed_output_format = profile.get('wavespeed_output_format', 'png')
        self.prompt_template = profile.get('prompt_template', 'bulk')
        self.trigger_name = profile.get('trigger_name', '')
        self.generate_captions = profile.get('generate_captions', False)
        self.openai_caption_model = profile.get('openai_caption_model', 'gpt-5.1')
        # Лимиты из профиля (если указаны)
        if profile.get('limit_ref_images'):
            self.limit_ref_images = profile.get('limit_ref_images')
        if profile.get('limit_sample_images'):
            self.limit_sample_images = profile.get('limit_sample_images')
    
    def save_to_profile(self, profile_name: str, description: str = ""):
        """Сохраняет текущие настройки в профиль (без API ключей, они в config.json)"""
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        # Проверяем, существует ли профиль
        created_at = None
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    created_at = existing.get('created_at', datetime.now().isoformat())
            except:
                created_at = datetime.now().isoformat()
        else:
            created_at = datetime.now().isoformat()
        
        # Сохраняем только выбор провайдеров/моделей, не API ключи
        # (ключи хранятся в config.json)
        profile_data = {
            'name': profile_name,
            'description': description,
            'created_at': created_at,
            'updated_at': datetime.now().isoformat(),
            'ai_provider': self.ai_provider,
            'gemini_model': self.gemini_model,
            'openai_model': self.openai_model,
            'image_provider': self.image_provider,
            'wavespeed_size': self.wavespeed_size,
            'wavespeed_model': self.wavespeed_model,
            'wavespeed_resolution': self.wavespeed_resolution,
            'wavespeed_output_format': self.wavespeed_output_format,
            'prompt_template': self.prompt_template,
            'trigger_name': self.trigger_name,
            'generate_captions': self.generate_captions,
            'openai_caption_model': self.openai_caption_model,
            'limit_ref_images': self.limit_ref_images,
            'limit_sample_images': self.limit_sample_images,
            '_note': 'API ключи хранятся в config.json и не сохраняются в профилях'
        }
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        return profile_path
    
    def list_profiles(self) -> List[Dict]:
        """Возвращает список всех сохраненных профилей"""
        profiles = []
        if not self.profiles_dir.exists():
            return profiles
        
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                profiles.append({
                    'name': profile.get('name', profile_file.stem),
                    'description': profile.get('description', ''),
                    'file': profile_file.stem
                })
            except:
                continue
        
        return sorted(profiles, key=lambda x: x['name'])
    
    def get_minimal_config(self) -> Dict:
        """Возвращает минимальную конфигурацию (пути и API ключи)"""
        return {
            'influencer_ref_folder': './Influencer Reference Images',
            'sample_dataset_folder': './Sample Dataset',
            'output_folder': './output',
            'limit_ref_images': 10,
            'limit_sample_images': 10,
            'gemini_api_key': '',
            'openai_api_key': '',
            'wavespeed_api_key': ''
        }
    
    def save_base_config(self, config: Dict):
        """Сохраняет базовую конфигурацию (только пути)"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def to_dict(self) -> Dict:
        """Преобразует конфигурацию в словарь для сохранения"""
        return {
            'ai_provider': self.ai_provider,
            'gemini_api_key': self.gemini_api_key,
            'gemini_model': self.gemini_model,
            'openai_api_key': self.openai_api_key,
            'openai_model': self.openai_model,
            'image_provider': self.image_provider,
            'wavespeed_api_key': self.wavespeed_api_key,
            'wavespeed_size': self.wavespeed_size,
            'wavespeed_model': self.wavespeed_model,
            'wavespeed_resolution': self.wavespeed_resolution,
            'wavespeed_output_format': self.wavespeed_output_format,
            'prompt_template': self.prompt_template,
            'limit_ref_images': self.limit_ref_images,
            'limit_sample_images': self.limit_sample_images
        }


class LocalFileManager:
    """Управление локальными файлами вместо Dropbox"""
    
    @staticmethod
    def list_image_files(folder_path: str, limit: int = 10) -> List[Dict]:
        """Список изображений в папке"""
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Папка не найдена: {folder_path}")
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        files = []
        
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                files.append({
                    'id': str(file_path),
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size
                })
                if len(files) >= limit:
                    break
        
        return files
    
    @staticmethod
    def read_file(file_path: str) -> Tuple[bytes, str]:
        """Читает файл и возвращает данные и имя файла"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        with open(path, 'rb') as f:
            data = f.read()
        
        return data, path.name
    
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """Определяет MIME тип файла"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'image/jpeg'


class PromptGenerator:
    """Генератор промптов используя Gemini или OpenAI"""
    
    def __init__(self, config: Config):
        self.config = config
        self.setup_provider()
    
    def setup_provider(self):
        """Настраивает выбранный AI провайдер"""
        if self.config.ai_provider == 'gemini':
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai не установлен. Установите: pip install google-generativeai")
            if not self.config.gemini_api_key:
                raise ValueError("Gemini API ключ не установлен в конфигурации")
            genai.configure(api_key=self.config.gemini_api_key)
            self.client = genai.GenerativeModel(self.config.gemini_model)
        
        elif self.config.ai_provider == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai не установлен. Установите: pip install openai")
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API ключ не установлен в конфигурации")
            self.client = OpenAI(api_key=self.config.openai_api_key)
        else:
            raise ValueError(f"Неизвестный AI провайдер: {self.config.ai_provider}")
    
    def generate_prompt(self, ref_images: List[bytes], sample_image: bytes) -> str:
        """Генерирует промпт на основе изображений"""
        # Используем один и тот же промпт для обоих шаблонов
        # Разница только в количестве обрабатываемых изображений
        # Получаем модель Wavespeed из конфига для правильного промпта
        wavespeed_model = getattr(self.config, 'wavespeed_model', '')
        prompt_text = self._get_prompt_template(wavespeed_model)
        
        if self.config.ai_provider == 'gemini':
            return self._generate_with_gemini(prompt_text, ref_images, sample_image)
        else:
            return self._generate_with_openai(prompt_text, ref_images, sample_image)
    
    def _get_prompt_template(self, wavespeed_model: str = '') -> str:
        """Детальный промпт, адаптированный под выбранную модель Wavespeed"""
        
        # Определяем модель и создаем соответствующий промпт
        model_name = ""
        model_version = ""
        
        if 'seedream-v4.5' in wavespeed_model.lower() or 'seedream-v4.5' in wavespeed_model:
            model_name = "Seedream v4.5"
            model_version = "4.5"
        elif 'seedream-v4' in wavespeed_model.lower() and 'v4.5' not in wavespeed_model.lower():
            model_name = "Seedream v4.0"
            model_version = "4.0"
        elif 'nano-banana' in wavespeed_model.lower() or 'nano-banana-pro' in wavespeed_model.lower():
            model_name = "Nano Banana Pro"
            model_version = "Pro"
        else:
            # По умолчанию используем Seedream 4.0
            model_name = "Seedream v4.0"
            model_version = "4.0"
        
        return f"""You are an expert prompt engineer specializing in the {model_name} AI model. You create complete, detailed, and technically precise image generation prompts.

Primary Directive: Your task is to analyze Reference Image 3 (a complete scene) and generate a single, comprehensive prompt for {model_name}. This prompt will instruct the model on how to use a total of three reference images.

Critical Context (Non-negotiable): {model_name} will always receive 3 reference images in this specific order:
Images 1 & 2: Provide the subject's complete face structure, facial features, and identity.
Image 3: The complete scene reference (this is the image you will be given to analyze).
Your analysis must focus exclusively on Image 3. Your generated prompt must correctly instruct {model_name} on this specific 3-image workflow.

Your Generation Task:
You will be given Image 3.
You will analyze Image 3 ONLY.
You will output ONLY the complete, formatted prompt for {model_name}. Do not add any conversational preamble, explanation, or text outside the specified format.

Mandatory Output Format (Strict Template):
Use the first two reference images for the subject's complete face, features, and identity. Use reference image 3 as the complete reference for all other elements: clothing, pose, action, body type, scene composition, background environment, lighting, and overall atmosphere.

Subject details: [Describe the subject's clothing in exhaustive detail: every visible garment (e.g., shirt, jacket, trousers, dress), accessories (e.g., hat, scarf, belt, bag), jewelry (e.g., necklace, earrings, rings, watch), and footwear. Specify colors, patterns, textures (e.g., denim, silk, wool, leather), cuts (e.g., loose-fitting, tailored), and styles (e.g., formal, casual, athletic)]. [Describe the exact pose: sitting, standing, leaning. Detail the position of the torso, arms (e.g., folded, extended, one hand in pocket), legs (e.g., crossed, straight), and head (e.g., tilted, looking forward)]. [Describe the subject's action or gesture (e.g., holding a cup, pointing, walking, reading) and overall body language. Describe the facial expression type (e.g., a wide smile, a serious expression, a thoughtful look, a laugh) but NOT the features.]

The scene: [Describe the location type (e.g., a city street, a living room, a forest, an office)]. The environment features [describe all significant background and foreground elements: architectural details (e.g., buildings, windows, walls), furniture (e.g., chairs, tables, lamps), props (e.g., books, plants, cars), and natural elements (e.g., trees, mountains, water)]. The setting is [describe the spatial layout, e.g., "indoors in a cluttered studio," "outdoors on a crowded beach"].

Lighting: [Describe the lighting in technical detail: identify the primary light source(s) (e.g., sun, studio softbox, window, lamp), its direction (e.g., side-lit, backlit, overhead, three-point lighting), its quality (e.g., hard, soft, diffused), and the resulting shadows (e.g., long and soft, sharp and deep). Note the time of day (e.g., golden hour, midday, night) and the overall color temperature (e.g., warm, cool, neutral).]

Camera: [Describe the camera's properties: the angle (e.g., eye-level, low-angle, high-angle, dutch angle), the shot type (e.g., full-body shot, medium shot, cowboy shot), the depth of field (e.g., shallow with heavy bokeh, deep with everything in focus), and the overall composition (e.g., rule of thirds, centered, leading lines).]

Atmosphere: [Describe the mood or ambiance of the scene (e.g., serene, chaotic, melancholic, energetic, professional, mysterious). If outdoors, note weather conditions (e.g., sunny, overcast, rainy, foggy) or environmental effects (e.g., lens flare, mist).]

Colors and textures: [Describe the dominant color palette of the entire image (e.g., monochrome with a blue tint, vibrant analogous colors, muted complementary colors). Highlight key materials and their surface textures (e.g., smooth glass, rough brick, shiny metal, matte fabric, glossy paint).]

Technical quality: [Describe the image's aesthetic and technical style, e.g., high-resolution, photorealistic, sharp focus, professional studio photography, cinematic, 35mm film grain, editorial fashion shot, candid.]

CRITICAL RULES (ABSOLUTE):
DO use generic terms: "this person," "the subject," "the individual."
DO be extremely detailed about clothing, accessories, pose, and background elements. These are your primary focus.
DO describe the type of facial expression (e.g., smiling, frowning, pensive) as this is part of the "pose" and "action."
NEVER describe: hair color, hair style, eye color, facial features, skin tone, ethnic features
Be extremely detailed about clothing and accessories
Be precise about pose and body position
Focus on EVERYTHING visible except facial/hair features
Output ONLY the formatted prompt, nothing else."""
    
    def _generate_with_gemini(self, prompt_text: str, ref_images: List[bytes], sample_image: bytes) -> str:
        """Генерация промпта через Gemini"""
        # Подготовка контента
        parts = [prompt_text]
        
        # Добавляем референсные изображения (первые 2)
        for img_data in ref_images[:2]:
            parts.append({
                'mime_type': 'image/jpeg',
                'data': img_data
            })
        
        # Добавляем sample изображение (третье)
        parts.append({
            'mime_type': 'image/jpeg',
            'data': sample_image
        })
        
        response = self.client.generate_content(parts)
        return response.text.strip()
    
    def _generate_with_openai(self, prompt_text: str, ref_images: List[bytes], sample_image: bytes) -> str:
        """Генерация промпта через OpenAI"""
        import base64
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text}
            ]
        }]
        
        # Добавляем референсные изображения
        for img_data in ref_images[:2]:
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            })
        
        # Добавляем sample изображение
        sample_b64 = base64.b64encode(sample_image).decode('utf-8')
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{sample_b64}"
            }
        })
        
        # Для GPT-5 моделей используется max_completion_tokens вместо max_tokens
        model = self.config.openai_model
        response_params = {
            'model': model,
            'messages': messages
        }
        
        # Определяем, какая модель используется
        # Увеличиваем лимит для длинных промптов
        if 'gpt-5' in model.lower() or 'gpt-4o' in model.lower():
            response_params['max_completion_tokens'] = 35000
        else:
            # Для старых моделей используем max_tokens
            response_params['max_tokens'] = 35000
        
        response = self.client.chat.completions.create(**response_params)
        
        # Безопасное извлечение промпта с детальной диагностикой
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            message = choice.message
            
            # Проверяем finish_reason
            finish_reason = getattr(choice, 'finish_reason', None)
            if finish_reason == 'length':
                print(f"   ⚠️  Внимание: Ответ был обрезан из-за лимита токенов (finish_reason: length)")
                if hasattr(response, 'usage') and response.usage:
                    print(f"   Использовано completion tokens: {response.usage.completion_tokens}")
                    print(f"   Лимит: {response_params.get('max_completion_tokens', response_params.get('max_tokens', 'N/A'))}")
            
            # Извлекаем контент разными способами
            message_content = getattr(message, 'content', None)
            
            if message_content:
                prompt = message_content.strip()
                if prompt:
                    return prompt
                else:
                    print(f"   ⚠️  Внимание: OpenAI вернул пустую строку для промпта. Модель: {model}")
                    print(f"   Finish reason: {finish_reason}")
                    return ""
            else:
                print(f"   ⚠️  Внимание: OpenAI вернул None для message.content. Модель: {model}")
                print(f"   Finish reason: {finish_reason}")
                print(f"   Message type: {type(message)}")
                print(f"   Message attributes: {[attr for attr in dir(message) if not attr.startswith('_')]}")
                return ""
        else:
            print(f"   ⚠️  Ошибка: OpenAI не вернул choices для промпта. Модель: {model}")
            return ""


class ImageGenerator:
    """Генератор изображений через Wavespeed"""
    
    def __init__(self, config: Config):
        self.config = config
        self.setup_provider()
    
    def setup_provider(self):
        """Настраивает выбранный провайдер генерации изображений"""
        if self.config.image_provider == 'wavespeed':
            if not self.config.wavespeed_api_key:
                raise ValueError("Wavespeed API ключ не установлен в конфигурации")
        else:
            raise ValueError(f"Неизвестный провайдер генерации: {self.config.image_provider}")
    
    def generate_image(self, ref_images: List[bytes], sample_image: bytes, prompt: str, output_path: str):
        """Генерирует изображение/видео и сохраняет его"""
        if self.config.image_provider == 'wavespeed':
            self._generate_with_wavespeed(ref_images, sample_image, prompt, output_path)
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {self.config.image_provider}")
    
    def _generate_with_wavespeed(self, ref_images: List[bytes], sample_image: bytes, prompt: str, output_path: str):
        """Генерация через Wavespeed API с поддержкой разных моделей"""
        model = self.config.wavespeed_model
        
        # Определяем тип модели и endpoint
        if 'image-to-video' in model or '/video' in model:
            self._generate_video_wavespeed(ref_images, sample_image, prompt, output_path, model)
        else:
            # Все модели поддерживают image-to-image (edit, seedream)
            self._generate_image_edit_wavespeed(ref_images, sample_image, prompt, output_path, model)
    
    def _generate_image_edit_wavespeed(self, ref_images: List[bytes], sample_image: bytes, prompt: str, output_path: str, model: str):
        """Генерация через Wavespeed Image-to-Image API (edit модели)"""
        # Формируем URL для модели (заменяем / на правильный формат)
        model_path = model
        url = f"https://api.wavespeed.ai/api/v3/{model_path}"
        
        # Подготовка изображений в base64
        images_base64 = []
        for img_data in ref_images[:2]:
            images_base64.append(base64.b64encode(img_data).decode('utf-8'))
        images_base64.append(base64.b64encode(sample_image).decode('utf-8'))
        
        # Очистка промпта от переносов строк
        clean_prompt = prompt.replace('\n', ' ').replace('\r', ' ')
        
        payload = {
            "enable_base64_output": False,
            "enable_sync_mode": True,  # Синхронный режим для получения результата сразу
            "images": images_base64,
            "prompt": clean_prompt
        }
        
        # Добавляем дополнительные параметры если нужно
        if hasattr(self.config, 'wavespeed_resolution') and self.config.wavespeed_resolution:
            payload["resolution"] = self.config.wavespeed_resolution
        if hasattr(self.config, 'wavespeed_output_format') and self.config.wavespeed_output_format:
            payload["output_format"] = self.config.wavespeed_output_format
        if hasattr(self.config, 'wavespeed_size') and self.config.wavespeed_size and 'size' not in payload:
            # Для некоторых моделей используется size вместо resolution
            if '*' in self.config.wavespeed_size:
                width, height = self.config.wavespeed_size.split('*')
                payload["width"] = int(width)
                payload["height"] = int(height)
            else:
                payload["size"] = self.config.wavespeed_size
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.wavespeed_api_key}"
        }
        
        response = self._make_wavespeed_request(url, payload, headers, output_path, is_video=False)
        return response
    
    def _generate_video_wavespeed(self, ref_images: List[bytes], sample_image: bytes, prompt: str, output_path: str, model: str):
        """Генерация видео через Wavespeed Image-to-Video API"""
        model_path = model
        url = f"https://api.wavespeed.ai/api/v3/{model_path}"
        
        # Для video используем sample_image как основное изображение
        image_base64 = base64.b64encode(sample_image).decode('utf-8')
        
        # Очистка промпта
        clean_prompt = prompt.replace('\n', ' ').replace('\r', ' ')
        
        payload = {
            "enable_base64_output": False,
            "enable_sync_mode": False,  # Видео обычно асинхронное
            "image": image_base64,
            "prompt": clean_prompt
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.wavespeed_api_key}"
        }
        
        response = self._make_wavespeed_request(url, payload, headers, output_path, is_video=True)
        return response
    
    def _make_wavespeed_request(self, url: str, payload: Dict, headers: Dict, output_path: str, is_video: bool = False):
        """Выполняет запрос к Wavespeed API с обработкой ошибок"""
        i18n = get_i18n()
        # Настройка retry стратегии
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,  # Увеличено с 1 до 2 для более длительных задержек
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Увеличиваем таймаут для image-to-image (может занимать больше времени)
        timeout_seconds = 900 if is_video else 600  # 15 минут для видео, 10 минут для изображений
        
        try:
            response = session.post(url, json=payload, headers=headers, timeout=timeout_seconds)
            response.raise_for_status()
            result = response.json()
            
            # Обработка формата ответа Wavespeed с оберткой {code, message, data}
            if 'data' in result:
                data = result['data']
                # Проверяем статус
                if data.get('status') == 'failed' or data.get('error'):
                    i18n = get_i18n()
                    error_msg = data.get('error', i18n.t('unknown_error'))
                    raise RuntimeError(i18n.t('wavespeed_api_error', error=error_msg))
                # Извлекаем данные из data
                result = data
            
            # Сохранение результата
            if is_video:
                # Для видео
                video_url = None
                if 'video' in result:
                    video_url = result.get('video')
                elif 'video_url' in result:
                    video_url = result.get('video_url')
                elif 'outputs' in result and isinstance(result['outputs'], list) and len(result['outputs']) > 0:
                    # Wavespeed возвращает массив URL в outputs
                    video_url = result['outputs'][0]
                
                if video_url:
                    video_response = requests.get(video_url, timeout=300)
                    video_response.raise_for_status()
                    # Определяем расширение из URL или используем mp4
                    ext = 'mp4'
                    if '.' in video_url:
                        ext = video_url.split('.')[-1].split('?')[0]
                    output_path = output_path.replace('.png', f'.{ext}').replace('.jpg', f'.{ext}')
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                elif 'video_base64' in result:
                    video_data = base64.b64decode(result['video_base64'])
                    output_path = output_path.replace('.png', '.mp4').replace('.jpg', '.mp4')
                    with open(output_path, 'wb') as f:
                        f.write(video_data)
                else:
                    # Сохраняем ответ для отладки
                    with open(output_path.replace('.png', '_response.json').replace('.mp4', '_response.json'), 'w') as f:
                        json.dump(result, f, indent=2)
                    raise ValueError(f"Неожиданный формат ответа для видео: {result.keys()}")
            else:
                # Для изображений
                image_url = None
                if 'image' in result:
                    image_url = result.get('image')
                elif 'image_url' in result:
                    image_url = result.get('image_url')
                elif 'outputs' in result and isinstance(result['outputs'], list) and len(result['outputs']) > 0:
                    # Wavespeed возвращает массив URL в outputs
                    image_url = result['outputs'][0]
                
                if image_url:
                    img_response = requests.get(image_url, timeout=300)
                    img_response.raise_for_status()
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                elif 'image_base64' in result:
                    img_data = base64.b64decode(result['image_base64'])
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                else:
                    # Сохраняем ответ для отладки
                    with open(output_path.replace('.png', '_response.json').replace('.jpg', '_response.json'), 'w') as f:
                        json.dump(result, f, indent=2)
                    raise ValueError(f"Неожиданный формат ответа для изображения: {result.keys()}")
            
            return result
            
        except requests.exceptions.Timeout as e:
            i18n = get_i18n()
            error_msg = i18n.t('wavespeed_timeout_error', timeout=timeout_seconds)
            if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
                error_msg += f"\n{i18n.t('server_response')}: {e.response.text[:200]}"
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            i18n = get_i18n()
            error_msg = i18n.t('wavespeed_request_error', error=str(e))
            if hasattr(e, 'response') and e.response is not None:
                if hasattr(e.response, 'status_code'):
                    error_msg += f" (HTTP {e.response.status_code})"
                if hasattr(e.response, 'text'):
                    # Ограничиваем длину ответа сервера
                    server_response = e.response.text[:500]
                    error_msg += f"\n{i18n.t('server_response')}: {server_response}"
            raise RuntimeError(error_msg)


class CaptionGenerator:
    """Генератор подписей (captions) для LoRA обучения через OpenAI"""
    
    def __init__(self, config: Config):
        self.config = config
        if not OPENAI_AVAILABLE:
            raise ImportError("openai не установлен. Установите: pip install openai")
        if not config.openai_api_key:
            raise ValueError("OpenAI API ключ не установлен в конфигурации")
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def generate_caption(self, image_path: str, trigger_name: str) -> str:
        """Генерирует подпись для изображения"""
        import base64
        
        # Читаем изображение
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Конвертируем в base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Создаем промпт для генерации подписи
        prompt_text = f"""These are photos of {trigger_name}, analyze those images and caption them correctly for a LoRA training using "{trigger_name}" as the caption token. 

Be detailed and describe all aspects of the character visible in the image:
- Clothing and accessories (every detail)
- Pose and body position
- Action and gesture
- Scene and environment
- Lighting and atmosphere
- Colors and textures

Important: Use "{trigger_name}" as the main token. Be specific about features (e.g., "{trigger_name} with blonde hair" instead of just "{trigger_name}") so those traits become part of the character's identity.

Output ONLY the caption text, nothing else. Do not include file names or any other text."""
        
        # Используем специальную модель для captions, если указана, иначе используем основную модель
        caption_model = getattr(self.config, 'openai_caption_model', None) or self.config.openai_model
        
        # Для GPT-5 моделей используется max_completion_tokens вместо max_tokens
        response_params = {
            'model': caption_model,
            'messages': [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ]
        }
        
        # Определяем, какая модель используется
        if 'gpt-5' in caption_model.lower() or 'gpt-4o' in caption_model.lower():
            response_params['max_completion_tokens'] = 500
        else:
            # Для старых моделей используем max_tokens
            response_params['max_tokens'] = 500
        
        # Отправляем запрос к OpenAI
        response = self.client.chat.completions.create(**response_params)
        
        # Безопасное извлечение caption
        if response.choices and len(response.choices) > 0:
            message_content = response.choices[0].message.content
            if message_content:
                caption = message_content.strip()
            else:
                caption = ""
                print(f"   ⚠️  Внимание: Модель {caption_model} вернула пустой ответ. Возможно, модель не поддерживает анализ изображений (vision).")
        else:
            caption = ""
            print(f"   ⚠️  Ошибка: Модель {caption_model} не вернула ответ.")
        
        return caption


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
            
            # Загружаем все доступные изображения для выбора
            all_sample_files = self.file_manager.list_image_files(
                self.config.sample_dataset_folder,
                limit
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
            
            sample_files = self.file_manager.list_image_files(
                self.config.sample_dataset_folder,
                limit
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


def select_or_create_profile() -> Optional[str]:
    """Выбор существующего профиля или создание нового"""
    i18n = get_i18n()
    config = Config()
    profiles = config.list_profiles()
    
    print("\n" + "="*60)
    print(f"  📋 {i18n.t('profile_management')}")
    print("="*60)
    
    if profiles:
        print(f"\n{i18n.t('found_profiles', count=len(profiles))}\n")
        for idx, profile in enumerate(profiles, 1):
            desc = f" - {profile['description']}" if profile.get('description') else ""
            print(f"   [{idx}] {profile['name']}{desc}")
        print(f"   [0] {i18n.t('create_new_profile')}")
        print(f"   [Enter] {i18n.t('skip_use_temporary')}")
        
        choice = input(f"\n{i18n.t('your_choice')}: ").strip()
        
        if choice == '0' or choice.lower() == 'new':
            return None  # Создать новый
        elif choice == '':
            return None  # Пропустить
        elif choice.isdigit() and 1 <= int(choice) <= len(profiles):
            selected = profiles[int(choice) - 1]
            print(f"\n✓ {i18n.t('selected_profile', name=selected['name'])}")
            return selected['file']
        else:
            print(f"⚠ {i18n.t('invalid_choice_create_new')}")
            return None
    else:
        print(f"\n{i18n.t('no_profiles_saved')}")
        print(f"   [1] {i18n.t('create_new_profile')}")
        print(f"   [Enter] {i18n.t('skip_use_temporary')}")
        
        choice = input(f"\n{i18n.t('your_choice')}: ").strip()
        if choice == '1':
            return None  # Создать новый
        else:
            return None  # Пропустить


def save_profile_menu(config: Config):
    """Меню сохранения профиля"""
    i18n = get_i18n()
    print("\n" + "="*60)
    print(f"  💾 {i18n.t('save_profile_title')}")
    print("="*60)
    print(f"\n{i18n.t('want_to_save_profile')}")
    print(f"   [1] {i18n.t('yes_save')}")
    print(f"   [2] {i18n.t('no_skip')}")
    
    i18n = get_i18n()
    choice = input(f"\n{i18n.t('your_choice')} (1/2): ").strip()
    
    if choice == '1':
        # Запрашиваем имя профиля
        print(f"\n{i18n.t('enter')} {i18n.t('profile_name').lower()} (латиница, без пробелов):")
        print("   Примеры: 'production', 'test', 'video-generation'")
        profile_name = input(f"{i18n.t('profile_name')}: ").strip()
        
        if not profile_name:
            i18n = get_i18n()
            print(f"⚠ {i18n.t('profile_name')} не может быть пустым, пропускаем сохранение")
            return
        
        # Очищаем имя от недопустимых символов
        import re
        profile_name = re.sub(r'[^a-zA-Z0-9_-]', '_', profile_name)
        
        # Проверяем, существует ли профиль
        existing_profiles = config.list_profiles()
        profile_exists = any(p['file'] == profile_name for p in existing_profiles)
        
        if profile_exists:
            i18n = get_i18n()
            print(f"\n⚠ {i18n.t('profile_already_exists', name=profile_name)}")
            print(f"   [1] {i18n.t('overwrite_existing')}")
            print(f"   [2] {i18n.t('cancel_saving')}")
            overwrite = input(f"   {i18n.t('your_choice')} (1/2): ").strip()
            if overwrite != '1':
                print(f"   → {i18n.t('saving_cancelled')}")
                return
        
        # Запрашиваем описание (опционально)
        i18n = get_i18n()
        print(f"\n{i18n.t('enter_profile_description')}")
        print(f"   {i18n.t('profile_description_example', example='Для генерации постеров с Seedream 4.5')}")
        description = input(f"{i18n.t('enter')}: ").strip()
        
        try:
            profile_path = config.save_to_profile(profile_name, description)
            i18n = get_i18n()
            if profile_exists:
                print(f"\n✅ {i18n.t('profile_updated', name=profile_name)}")
            else:
                print(f"\n✅ {i18n.t('profile_created', name=profile_name)}")
            print(f"   {i18n.t('profile_path', path=profile_path)}")
        except Exception as e:
            i18n = get_i18n()
            print(f"\n❌ {i18n.t('error_saving_profile', error=e)}")
            import traceback
            traceback.print_exc()
    else:
        i18n = get_i18n()
        print(f"\n→ {i18n.t('settings_not_saved')}")


def interactive_menu(config: Config) -> Config:
    """Интерактивное меню для выбора настроек"""
    i18n = get_i18n()
    print("\n" + "="*60)
    print(f"  🎨 {i18n.t('interactive_menu_title')}")
    print("="*60)
    print(f"\n{i18n.t('select_settings')}\n")
    
    # Выбор AI провайдера
    print(f"1️⃣  {i18n.t('ai_provider')}:")
    current_ai = config.ai_provider if config.ai_provider else i18n.t('not_selected')
    print(f"   {i18n.t('current_value')}: {current_ai}")
    print(f"\n   [1] Gemini (Google Gemini 2.5 Flash)")
    print(f"       ✓ {i18n.t('gemini_description_1')}")
    print(f"       ✓ {i18n.t('gemini_description_2')}")
    print(f"       ✓ {i18n.t('gemini_description_3')}")
    print(f"       ✓ {i18n.t('gemini_description_4')}")
    print(f"       ⚠️  {i18n.t('gemini_description_5')}")
    print(f"       💡 {i18n.t('gemini_description_6')}")
    print(f"\n   [2] OpenAI (GPT-5 mini)")
    print(f"       ✓ {i18n.t('openai_description_1')}")
    print(f"       ✓ {i18n.t('openai_description_2')}")
    print(f"       ✓ {i18n.t('openai_description_3')}")
    print(f"       ✓ {i18n.t('openai_description_4')}")
    print(f"       ✓ {i18n.t('openai_description_5')}")
    print(f"       ⚠️  {i18n.t('openai_description_6')}")
    print(f"       💡 {i18n.t('openai_description_7')}")
    choice = input(f"\n   {i18n.t('your_choice')} (1/2 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
    if choice == '1':
        config.ai_provider = 'gemini'
        print(f"   ✓ {i18n.t('selected')}: Gemini")
    elif choice == '2':
        config.ai_provider = 'openai'
        print(f"   ✓ {i18n.t('selected')}: OpenAI")
    else:
        if config.ai_provider:
            print(f"   → {i18n.t('using_value')}: {config.ai_provider}")
        else:
            print(f"   ⚠️  {i18n.t('ai_provider')} {i18n.t('not_selected')}! {i18n.t('select_option')}.")
            # Повторяем запрос если не выбран
            while not config.ai_provider:
                choice = input(f"   {i18n.t('your_choice')} (1/2, {i18n.t('must_select')}): ").strip()
                if choice == '1':
                    config.ai_provider = 'gemini'
                    print(f"   ✓ {i18n.t('selected')}: Gemini")
                elif choice == '2':
                    config.ai_provider = 'openai'
                    print(f"   ✓ {i18n.t('selected')}: OpenAI")
                else:
                    print(f"   ⚠️  {i18n.t('please_select_1_or_2')}")
    
    # Выбор шаблона промпта
    print(f"\n2️⃣  {i18n.t('processing_mode')}:")
    current_template = config.prompt_template if hasattr(config, 'prompt_template') and config.prompt_template else "bulk"
    print(f"   {i18n.t('current_value')}: {current_template}")
    print(f"\n   ⚠️  {i18n.t('prompt_same_note')}")
    print(f"   {i18n.t('prompt_difference_note')}\n")
    print(f"   [1] {i18n.t('bulk_mode_title')}")
    print(f"       📊 {i18n.t('bulk_mode_1')}")
    print(f"       📋 {i18n.t('bulk_mode_2')}")
    print(f"       📝 {i18n.t('bulk_mode_3')}")
    print(f"       ✓ {i18n.t('bulk_mode_4')}")
    print(f"       ✓ {i18n.t('bulk_mode_5')}")
    print(f"       💡 {i18n.t('bulk_mode_6')}")
    print(f"\n   [2] {i18n.t('detailed_mode_title')}")
    print(f"       📊 {i18n.t('detailed_mode_1')}")
    print(f"       📋 {i18n.t('detailed_mode_2')}")
    print(f"       📝 {i18n.t('detailed_mode_3')}")
    print(f"       ✓ {i18n.t('detailed_mode_4')}")
    print(f"       ✓ {i18n.t('detailed_mode_5')}")
    print(f"       💡 {i18n.t('detailed_mode_6')}")
    choice = input(f"\n   {i18n.t('your_choice')} (1/2 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
    if choice == '1':
        config.prompt_template = 'bulk'
        print(f"   ✓ {i18n.t('selected')}: bulk")
    elif choice == '2':
        config.prompt_template = 'detailed'
        print(f"   ✓ {i18n.t('selected')}: detailed")
    else:
        print(f"   → {i18n.t('using_value')} из config: {config.prompt_template}")
    
    # Выбор провайдера генерации
    print(f"\n3️⃣  {i18n.t('image_generation_provider')}:")
    current_provider = config.image_provider if config.image_provider else i18n.t('not_selected')
    print(f"   {i18n.t('current_value')}: {current_provider}")
    print(f"\n   [1] Wavespeed")
    print(f"       ✓ {i18n.t('wavespeed_description_1')}")
    print(f"       ✓ {i18n.t('wavespeed_description_2')}")
    print(f"       ✓ {i18n.t('wavespeed_description_3')}")
    print(f"       ✓ {i18n.t('wavespeed_description_4')}")
    print(f"       ✓ {i18n.t('wavespeed_description_5')}")
    print(f"       💡 {i18n.t('wavespeed_description_6')}")
    choice = input(f"\n   {i18n.t('your_choice')} (1 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
    if choice == '1':
        config.image_provider = 'wavespeed'
        print(f"   ✓ {i18n.t('selected')}: Wavespeed")
    else:
        if config.image_provider:
            print(f"   → {i18n.t('using_value')}: {config.image_provider}")
        else:
            print(f"   ⚠️  {i18n.t('image_generation_provider')} {i18n.t('not_selected')}! {i18n.t('select_option')}.")
            # Повторяем запрос если не выбран
            while not config.image_provider:
                choice = input(f"   {i18n.t('your_choice')} (1, {i18n.t('must_select')}): ").strip()
                if choice == '1':
                    config.image_provider = 'wavespeed'
                    print(f"   ✓ {i18n.t('selected')}: Wavespeed")
                else:
                    print(f"   ⚠️  {i18n.t('please_select_1')}")
    
    # Выбор модели Wavespeed
    if config.image_provider == 'wavespeed':
        print(f"\n4️⃣  {i18n.t('wavespeed_model')}:")
        print(f"   {i18n.t('current_value')}: {config.wavespeed_model}")
        print(f"\n   {i18n.t('image_to_image')}")
        print("      [1] google/nano-banana-pro/edit")
        print(f"         • {i18n.t('nano_banana_1')}")
        print(f"         • {i18n.t('nano_banana_2')}")
        print(f"         • {i18n.t('nano_banana_3')}")
        print(f"         • {i18n.t('nano_banana_4')}")
        print(f"         • {i18n.t('nano_banana_5')}")
        print(f"         • {i18n.t('nano_banana_6')}")
        print(f"\n      [2] bytedance/seedream-v4.5")
        print(f"         • {i18n.t('seedream_v45_1')}")
        print(f"         • {i18n.t('seedream_v45_2')}")
        print(f"         • {i18n.t('seedream_v45_3')}")
        print(f"         • {i18n.t('seedream_v45_4')}")
        print(f"         • {i18n.t('seedream_v45_5')}")
        print(f"         • {i18n.t('seedream_v45_6')}")
        print(f"         • {i18n.t('seedream_v45_7')}")
        print(f"\n      [3] bytedance/seedream-v4")
        print(f"         • {i18n.t('seedream_v4_1')}")
        print(f"         • {i18n.t('seedream_v4_2')}")
        print(f"         • {i18n.t('seedream_v4_3')}")
        print(f"         • {i18n.t('seedream_v4_4')}")
        print(f"         • {i18n.t('seedream_v4_5')}")
        print(f"         • {i18n.t('seedream_v4_6')}")
        print(f"         • {i18n.t('seedream_v4_7')}")
        print(f"\n   {i18n.t('image_to_video')}")
        print("      [4] alibaba/wan-2.5/image-to-video")
        print(f"         • {i18n.t('wan_25_1')}")
        print(f"         • {i18n.t('wan_25_2')}")
        print(f"         • {i18n.t('wan_25_3')}")
        print(f"\n      [5] kwaivgi/kling-v2.6-pro/image-to-video")
        print(f"         • {i18n.t('kling_v26_1')}")
        print(f"         • {i18n.t('kling_v26_2')}")
        print(f"         • {i18n.t('kling_v26_3')}")
        print(f"         • {i18n.t('kling_v26_4')}")
        print(f"\n      [6] kwaivgi/kling-v2.5-turbo-pro/image-to-video")
        print(f"         • {i18n.t('kling_v25_1')}")
        print(f"         • {i18n.t('kling_v25_2')}")
        print(f"         • {i18n.t('kling_v25_3')}")
        print(f"         • {i18n.t('kling_v25_4')}")
        choice = input("\n   Ваш выбор (1-6 или Enter для пропуска): ").strip()
        models = {
            '1': 'google/nano-banana-pro/edit',
            '2': 'bytedance/seedream-v4.5',
            '3': 'bytedance/seedream-v4',
            '4': 'alibaba/wan-2.5/image-to-video',
            '5': 'kwaivgi/kling-v2.6-pro/image-to-video',
            '6': 'kwaivgi/kling-v2.5-turbo-pro/image-to-video'
        }
        if choice in models:
            config.wavespeed_model = models[choice]
            print(f"   ✓ {i18n.t('selected')}: {config.wavespeed_model}")
        else:
            if config.wavespeed_model:
                print(f"   → {i18n.t('using_value')}: {config.wavespeed_model}")
            else:
                print(f"   ⚠️  {i18n.t('wavespeed_model')} {i18n.t('not_selected')}! {i18n.t('select_option')}.")
                # Повторяем запрос если не выбрана
                while not config.wavespeed_model:
                    choice = input(f"   {i18n.t('your_choice')} (1-6, {i18n.t('must_select')}): ").strip()
                    if choice in models:
                        config.wavespeed_model = models[choice]
                        print(f"   ✓ {i18n.t('selected')}: {config.wavespeed_model}")
                    else:
                        print(f"   ⚠️  {i18n.t('please_select_1_or_2')} (1-6)")
        
        # Дополнительные настройки для Wavespeed
        # Настройки разрешения для Nano Banana Pro и Seedream моделей
        if 'edit' in config.wavespeed_model or 'seedream' in config.wavespeed_model.lower():
            print("\n5️⃣  Разрешение для Wavespeed:")
            print(f"   Текущее значение: {config.wavespeed_resolution}")
            print("\n   [1] 1k (1024×1024 или аналогичное)")
            print(f"       ✓ {i18n.t('resolution_1k_1')}")
            print(f"       ✓ {i18n.t('resolution_1k_2')}")
            print(f"       ✓ {i18n.t('resolution_1k_3')}")
            print(f"       ⚠️  {i18n.t('resolution_1k_4')}")
            print(f"       💡 {i18n.t('resolution_1k_5')}")
            print("\n   [2] 2k (2048×2048 или аналогичное)")
            print(f"       ✓ {i18n.t('resolution_2k_1')}")
            print(f"       ✓ {i18n.t('resolution_2k_2')}")
            print(f"       ✓ {i18n.t('resolution_2k_3')}")
            print(f"       💡 {i18n.t('resolution_2k_4')}")
            print("\n   [3] 4k (4096×4096 или аналогичное)")
            print(f"       ✓ {i18n.t('resolution_4k_1')}")
            print(f"       ✓ {i18n.t('resolution_4k_2')}")
            print(f"       ⚠️  {i18n.t('resolution_4k_3')}")
            print(f"       ⚠️  {i18n.t('resolution_4k_4')}")
            print(f"       💡 {i18n.t('resolution_4k_5')}")
            choice = input(f"\n   {i18n.t('your_choice')} (1-3 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
            resolutions = {'1': '1k', '2': '2k', '3': '4k'}
            if choice in resolutions:
                config.wavespeed_resolution = resolutions[choice]
                print(f"   ✓ {i18n.t('selected')}: {config.wavespeed_resolution}")
            else:
                print(f"   → {i18n.t('using_value')} из config: {config.wavespeed_resolution}")
    
    # Настройки для генерации captions (LoRA)
    print(f"\n6️⃣  {i18n.t('caption_generation')}:")
    current_generate = i18n.t('yes') if config.generate_captions else i18n.t('no')
    print(f"   {i18n.t('current_value')}: {current_generate}")
    print(f"\n   {i18n.t('caption_generation_desc')}")
    print(f"\n   [1] {i18n.t('caption_generation_yes')}")
    print(f"       ✓ {i18n.t('caption_yes_1')}")
    print(f"       ✓ {i18n.t('caption_yes_2')}")
    print(f"       ✓ {i18n.t('caption_yes_3')}")
    print(f"       ⚠️  {i18n.t('caption_yes_4')}")
    print(f"       ⚠️  {i18n.t('caption_yes_5')}")
    print(f"       💡 {i18n.t('caption_yes_6')}")
    print(f"\n   [2] {i18n.t('caption_generation_no')}")
    print(f"       ✓ {i18n.t('caption_no_1')}")
    print(f"       ✓ {i18n.t('caption_no_2')}")
    print(f"       💡 {i18n.t('caption_no_3')}")
    choice = input(f"\n   {i18n.t('your_choice')} (1/2 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
    if choice == '1':
        config.generate_captions = True
        print(f"   ✓ {i18n.t('caption_enabled')}")
        
        # Запрашиваем trigger name
        print(f"\n7️⃣  {i18n.t('trigger_name_prompt')}:")
        current_trigger = config.trigger_name if config.trigger_name else i18n.t('not_selected')
        print(f"   {i18n.t('current_value')}: {current_trigger}")
        print(f"\n   {i18n.t('trigger_name_desc')}")
        print(f"   {i18n.t('trigger_name_examples')}")
        print(f"   ⚠️  {i18n.t('trigger_name_warning')}")
        trigger_input = input(f"\n   {i18n.t('enter')} trigger name ({i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
        if trigger_input:
            # Убираем пробелы и специальные символы
            trigger_name = trigger_input.replace(' ', '_').replace('-', '_')
            config.trigger_name = trigger_name
            print(f"   ✓ {i18n.t('trigger_name_set', name=trigger_name)}")
        else:
            if config.trigger_name:
                print(f"   → {i18n.t('using_value')} из config: {config.trigger_name}")
            else:
                print(f"   ⚠️  {i18n.t('trigger_name_not_set')}")
                config.generate_captions = False
        
        # Выбор модели OpenAI для генерации captions
        if config.generate_captions:
            print(f"\n8️⃣  {i18n.t('openai_caption_model')}:")
            current_caption_model = getattr(config, 'openai_caption_model', None) or config.openai_model or "gpt-5.1"
            print(f"   {i18n.t('current_value')}: {current_caption_model}")
            print("\n   [1] gpt-5.1")
            print(f"       ✓ {i18n.t('gpt51_caption_1')}")
            print(f"       ✓ {i18n.t('gpt51_caption_2')}")
            print(f"       ✓ {i18n.t('gpt51_caption_3')}")
            print(f"       ✓ {i18n.t('gpt51_caption_4')}")
            print(f"       ✓ {i18n.t('gpt51_caption_5')}")
            print(f"\n   [2] gpt-4o ({i18n.t('gpt4o_caption_1')})")
            print(f"       ✓ {i18n.t('gpt4o_caption_1')}")
            print(f"       ✓ {i18n.t('gpt4o_caption_2')}")
            print(f"       ✓ {i18n.t('gpt4o_caption_3')}")
            print(f"       ✓ {i18n.t('gpt4o_caption_4')}")
            print(f"       ✓ {i18n.t('gpt4o_caption_5')}")
            print(f"\n   ⚠️  {i18n.t('caption_models_note')}")
            choice = input(f"\n   {i18n.t('your_choice')} (1-2 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
            models = {
                '1': 'gpt-5.1',
                '2': 'gpt-4o'
            }
            if choice in models:
                config.openai_caption_model = models[choice]
                print(f"   ✓ {i18n.t('selected')}: {config.openai_caption_model}")
            else:
                if hasattr(config, 'openai_caption_model') and config.openai_caption_model:
                    print(f"   → {i18n.t('using_value')} из config: {config.openai_caption_model}")
                else:
                    config.openai_caption_model = 'gpt-5.1'
                    print(f"   → {i18n.t('using_value')} по умолчанию: {config.openai_caption_model}")
    elif choice == '2':
        config.generate_captions = False
        print(f"   ✓ {i18n.t('caption_disabled')}")
    else:
        if config.generate_captions:
            print(f"   → {i18n.t('using_value')} из config: {i18n.t('yes') if config.generate_captions else i18n.t('no')}")
            if config.generate_captions and not config.trigger_name:
                print(f"   ⚠️  {i18n.t('trigger_name_warning_caption')}")
    
    i18n = get_i18n()
    print("\n" + "="*60)
    print(f"  ✅ {i18n.t('settings_selected')}")
    print("="*60)
    print(f"\n📋 {i18n.t('final_settings')}")
    print(f"   {i18n.t('ai_provider')}: {config.ai_provider}")
    print(f"   {i18n.t('prompt_template')}: {config.prompt_template}")
    print(f"   {i18n.t('image_generation_provider')}: {config.image_provider}")
    if config.image_provider == 'wavespeed':
        print(f"   {i18n.t('wavespeed_model')}: {config.wavespeed_model}")
    if config.generate_captions:
        print(f"   {i18n.t('caption_generation')}: {i18n.t('yes')}")
        print(f"   {i18n.t('trigger_name')}: {config.trigger_name if config.trigger_name else i18n.t('not_selected')}")
        caption_model = getattr(config, 'openai_caption_model', None) or config.openai_model or 'gpt-5.1'
        print(f"   {i18n.t('openai_caption_model')}: {caption_model}")
    else:
        print(f"   {i18n.t('caption_generation')}: {i18n.t('no')}")
    print("\n")
    
    return config


def select_language():
    """Выбор языка интерфейса"""
    if not I18N_AVAILABLE:
        return
    
    # Пытаемся загрузить язык из config.json
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                lang = config.get('language', '').lower()
                if lang in ['ru', 'en']:
                    set_language(lang)
                    return
    except:
        pass
    
    # Предлагаем выбрать язык
    print("=" * 60)
    print("  🌍 Select Language / Выберите язык")
    print("=" * 60)
    print("\n[1] English")
    print("[2] Русский")
    print("\n[Enter] Use default (Russian) / Использовать по умолчанию (Русский)")
    
    choice = input("\nYour choice / Ваш выбор (1/2 или Enter): ").strip()
    
    if choice == '1':
        set_language('en')
        print("✓ Language set to English")
    elif choice == '2':
        set_language('ru')
        print("✓ Язык установлен: Русский")
    else:
        set_language('ru')
        print("→ Используется язык по умолчанию: Русский")
    
    print()


def main():
    """Главная функция"""
    # Выбор языка в самом начале
    select_language()
    
    parser = argparse.ArgumentParser(
        description='Dataset Creation Bulk - Python аналог Make.com workflow'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Путь к файлу конфигурации (по умолчанию: config.json)'
    )
    parser.add_argument(
        '--profile',
        type=str,
        help='Имя профиля для использования (пропускает выбор профиля)'
    )
    parser.add_argument(
        '--ai-provider',
        choices=['gemini', 'openai'],
        help='AI провайдер для генерации промптов (переопределяет config)'
    )
    parser.add_argument(
        '--image-provider',
        choices=['wavespeed'],
        help='Провайдер для генерации изображений (переопределяет config)'
    )
    parser.add_argument(
        '--interactive',
        '-i',
        action='store_true',
        help='Запустить интерактивное меню для выбора настроек'
    )
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Пропустить интерактивное меню (использовать только config и аргументы)'
    )
    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='Показать список сохраненных профилей и выйти'
    )
    
    args = parser.parse_args()
    
    # Показать список профилей и выйти
    if args.list_profiles:
        i18n = get_i18n()
        config = Config(args.config)
        profiles = config.list_profiles()
        if profiles:
            print(f"\n📋 {i18n.t('found_profiles', count=len(profiles))}\n")
            for profile in profiles:
                desc = f" - {profile['description']}" if profile.get('description') else ""
                print(f"   • {profile['name']}{desc}")
        else:
            print(f"\n📋 {i18n.t('no_profiles_saved')}")
        return
    
    # Выбор профиля (если не указан --no-interactive и не указан --profile)
    selected_profile = None
    if not args.no_interactive and not args.profile:
        try:
            selected_profile = select_or_create_profile()
        except KeyboardInterrupt:
            print("\n\n❌ Прервано пользователем")
            return
        except Exception as e:
            print(f"\n⚠ Ошибка при выборе профиля: {e}")
            print("Продолжаем без профиля...\n")
    
    # Загружаем конфигурацию
    if args.profile:
        # Используем указанный профиль
        try:
            config = Config(args.config, profile_name=args.profile)
            print(f"✓ Загружен профиль: {args.profile}")
        except FileNotFoundError:
            print(f"❌ Профиль '{args.profile}' не найден")
            return
    elif selected_profile:
        # Используем выбранный профиль
        config = Config(args.config, profile_name=selected_profile)
    else:
        # Создаем новую конфигурацию (минимальную)
        config = Config(args.config)
    
    # Переопределяем провайдеры если указаны в аргументах
    if args.ai_provider:
        config.ai_provider = args.ai_provider
    if args.image_provider:
        config.image_provider = args.image_provider
    
    # Интерактивное меню (если не указан --no-interactive)
    if not args.no_interactive:
        if args.interactive or not any([args.ai_provider, args.image_provider, args.profile]):
            # Показываем меню если явно запрошено или если нет аргументов командной строки
            try:
                config = interactive_menu(config)
                # Предлагаем сохранить профиль (если не использовали существующий)
                if not selected_profile and not args.profile:
                    save_profile_menu(config)
            except KeyboardInterrupt:
                print("\n\n❌ Прервано пользователем")
                return
            except Exception as e:
                print(f"\n❌ Ошибка в интерактивном меню: {e}")
                import traceback
                traceback.print_exc()
                print("Продолжаем с минимальными настройками...\n")
    
    # Проверяем обязательные настройки
    if not config.ai_provider:
        print("❌ Ошибка: AI провайдер не выбран")
        print("   Выберите провайдера через интерактивное меню или укажите --ai-provider")
        return
    
    if not config.image_provider:
        print("❌ Ошибка: Провайдер генерации не выбран")
        print("   Выберите провайдера через интерактивное меню или укажите --image-provider")
        return
    
    # Создаем и запускаем обработку
    creator = DatasetCreator(config)
    creator.process_dataset()


if __name__ == '__main__':
    main()

