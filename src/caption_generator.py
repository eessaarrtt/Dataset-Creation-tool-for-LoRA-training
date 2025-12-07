"""Генератор подписей (captions) для LoRA обучения через OpenAI или Grok"""

import base64

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .config import Config


class CaptionGenerator:
    """Генератор подписей (captions) для LoRA обучения через OpenAI или Grok"""
    
    def __init__(self, config: Config):
        self.config = config
        # Определяем провайдера для captions
        caption_provider = getattr(config, 'caption_provider', 'openai')
        
        if caption_provider == 'grok':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai не установлен. Установите: pip install openai")
            if not config.grok_api_key:
                raise ValueError("Grok API ключ не установлен в конфигурации")
            # Grok использует OpenAI-совместимый API
            self.client = OpenAI(
                api_key=config.grok_api_key,
                base_url="https://api.x.ai/v1"
            )
            self.provider = 'grok'
        else:  # openai по умолчанию
            if not OPENAI_AVAILABLE:
                raise ImportError("openai не установлен. Установите: pip install openai")
            if not config.openai_api_key:
                raise ValueError("OpenAI API ключ не установлен в конфигурации")
            self.client = OpenAI(api_key=config.openai_api_key)
            self.provider = 'openai'
    
    def generate_caption(self, image_path: str, trigger_name: str) -> str:
        """Генерирует подпись для изображения"""
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
        
        # Определяем модель для captions в зависимости от провайдера
        if self.provider == 'grok':
            # Для Grok используем специальную модель или модель по умолчанию
            caption_model = getattr(self.config, 'grok_caption_model', None) or self.config.grok_model
        else:
            # Для OpenAI используем специальную модель или модель по умолчанию
            caption_model = getattr(self.config, 'openai_caption_model', None) or self.config.openai_model
        
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
        
        # Определяем параметры токенов в зависимости от модели
        if 'grok' in caption_model.lower():
            response_params['max_completion_tokens'] = 500
        elif 'gpt-5' in caption_model.lower() or 'gpt-4o' in caption_model.lower():
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
                provider_name = "Grok" if self.provider == 'grok' else "OpenAI"
                print(f"   ⚠️  Внимание: Модель {caption_model} ({provider_name}) вернула пустой ответ. Возможно, модель не поддерживает анализ изображений (vision).")
        else:
            caption = ""
            provider_name = "Grok" if self.provider == 'grok' else "OpenAI"
            print(f"   ⚠️  Ошибка: Модель {caption_model} ({provider_name}) не вернула ответ.")
        
        return caption

