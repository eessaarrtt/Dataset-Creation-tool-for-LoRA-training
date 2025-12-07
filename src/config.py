"""Конфигурация приложения с поддержкой профилей"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


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
        self.grok_api_key = base_config.get('grok_api_key', '')
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
        self.openai_model = 'gpt-5.1'
        self.grok_model = 'grok-4-1-fast-reasoning'
        
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
        self.caption_provider = 'openai'  # Провайдер для captions: 'openai' или 'grok'
        self.openai_caption_model = 'gpt-5.1'  # Модель OpenAI для генерации captions
        self.grok_caption_model = 'grok-4-1-fast-reasoning'  # Модель Grok для генерации captions
        
        # Настройки для NSFW и обычного контента
        # Модели для промптов
        self.ai_provider_nsfw = None  # Провайдер для NSFW промптов
        self.ai_provider_normal = None  # Провайдер для обычных промптов
        self.gemini_model_nsfw = 'gemini-2.5-flash'
        self.gemini_model_normal = 'gemini-2.5-flash'
        self.openai_model_nsfw = 'gpt-5.1'
        self.openai_model_normal = 'gpt-5.1'
        self.grok_model_nsfw = 'grok-4-1-fast-reasoning'
        self.grok_model_normal = 'grok-4-1-fast-reasoning'
        
        # Модели для генерации изображений
        self.wavespeed_model_nsfw = ''
        self.wavespeed_model_normal = ''
        
        # Модели для captions
        self.caption_provider_nsfw = 'openai'
        self.caption_provider_normal = 'openai'
        self.openai_caption_model_nsfw = 'gpt-5.1'
        self.openai_caption_model_normal = 'gpt-5.1'
        self.grok_caption_model_nsfw = 'grok-4-1-fast-reasoning'
        self.grok_caption_model_normal = 'grok-4-1-fast-reasoning'
        
        # Флаг включения NSFW контента
        self.nsfw_enabled = False  # По умолчанию NSFW отключен
    
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
        self.openai_model = profile.get('openai_model', 'gpt-5.1')
        if profile.get('grok_api_key'):
            self.grok_api_key = profile.get('grok_api_key')
        self.grok_model = profile.get('grok_model', 'grok-4-1-fast-reasoning')
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
        self.caption_provider = profile.get('caption_provider', 'openai')
        self.openai_caption_model = profile.get('openai_caption_model', 'gpt-5.1')
        self.grok_caption_model = profile.get('grok_caption_model', 'grok-4-1-fast-reasoning')
        
        # Настройки для NSFW и обычного контента
        self.ai_provider_nsfw = profile.get('ai_provider_nsfw')
        self.ai_provider_normal = profile.get('ai_provider_normal')
        self.gemini_model_nsfw = profile.get('gemini_model_nsfw', 'gemini-2.5-flash')
        self.gemini_model_normal = profile.get('gemini_model_normal', 'gemini-2.5-flash')
        self.openai_model_nsfw = profile.get('openai_model_nsfw', 'gpt-5.1')
        self.openai_model_normal = profile.get('openai_model_normal', 'gpt-5.1')
        self.grok_model_nsfw = profile.get('grok_model_nsfw', 'grok-4-1-fast-reasoning')
        self.grok_model_normal = profile.get('grok_model_normal', 'grok-4-1-fast-reasoning')
        self.wavespeed_model_nsfw = profile.get('wavespeed_model_nsfw', '')
        self.wavespeed_model_normal = profile.get('wavespeed_model_normal', '')
        self.caption_provider_nsfw = profile.get('caption_provider_nsfw', 'openai')
        self.caption_provider_normal = profile.get('caption_provider_normal', 'openai')
        self.openai_caption_model_nsfw = profile.get('openai_caption_model_nsfw', 'gpt-5.1')
        self.openai_caption_model_normal = profile.get('openai_caption_model_normal', 'gpt-5.1')
        self.grok_caption_model_nsfw = profile.get('grok_caption_model_nsfw', 'grok-4-1-fast-reasoning')
        self.grok_caption_model_normal = profile.get('grok_caption_model_normal', 'grok-4-1-fast-reasoning')
        
        # Флаг включения NSFW контента
        self.nsfw_enabled = profile.get('nsfw_enabled', False)
        
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
            'grok_model': self.grok_model,
            'image_provider': self.image_provider,
            'wavespeed_size': self.wavespeed_size,
            'wavespeed_model': self.wavespeed_model,
            'wavespeed_resolution': self.wavespeed_resolution,
            'wavespeed_output_format': self.wavespeed_output_format,
            'prompt_template': self.prompt_template,
            'trigger_name': self.trigger_name,
            'generate_captions': self.generate_captions,
            'caption_provider': self.caption_provider,
            'openai_caption_model': self.openai_caption_model,
            'grok_caption_model': self.grok_caption_model,
            'ai_provider_nsfw': self.ai_provider_nsfw,
            'ai_provider_normal': self.ai_provider_normal,
            'gemini_model_nsfw': self.gemini_model_nsfw,
            'gemini_model_normal': self.gemini_model_normal,
            'openai_model_nsfw': self.openai_model_nsfw,
            'openai_model_normal': self.openai_model_normal,
            'grok_model_nsfw': self.grok_model_nsfw,
            'grok_model_normal': self.grok_model_normal,
            'wavespeed_model_nsfw': self.wavespeed_model_nsfw,
            'wavespeed_model_normal': self.wavespeed_model_normal,
            'caption_provider_nsfw': self.caption_provider_nsfw,
            'caption_provider_normal': self.caption_provider_normal,
            'openai_caption_model_nsfw': self.openai_caption_model_nsfw,
            'openai_caption_model_normal': self.openai_caption_model_normal,
            'grok_caption_model_nsfw': self.grok_caption_model_nsfw,
            'grok_caption_model_normal': self.grok_caption_model_normal,
            'nsfw_enabled': self.nsfw_enabled,
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
            'grok_api_key': '',
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
            'grok_api_key': self.grok_api_key,
            'grok_model': self.grok_model,
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

