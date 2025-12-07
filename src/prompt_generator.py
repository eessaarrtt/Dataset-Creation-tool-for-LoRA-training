"""Генератор промптов используя Gemini, OpenAI или Grok"""

import base64
from typing import List

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

from .config import Config


class PromptGenerator:
    """Генератор промптов используя Gemini, OpenAI или Grok"""
    
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
        
        elif self.config.ai_provider == 'grok':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai не установлен. Установите: pip install openai")
            if not self.config.grok_api_key:
                raise ValueError("Grok API ключ не установлен в конфигурации")
            # Grok использует OpenAI-совместимый API с base_url от xAI
            self.client = OpenAI(
                api_key=self.config.grok_api_key,
                base_url="https://api.x.ai/v1"
            )
        else:
            raise ValueError(f"Неизвестный AI провайдер: {self.config.ai_provider}")
    
    def generate_prompt(self, ref_images: List[bytes], sample_image: bytes) -> str:
        """Генерирует промпт на основе изображений"""
        # Используем один и тот же промпт для обоих шаблонов
        # Разница только в количестве обрабатываемых изображений
        # Получаем модель Wavespeed из конфига для правильного промпта
        wavespeed_model = getattr(self.config, 'wavespeed_model', '')
        
        # Для Grok используем специальный промпт-шаблон
        if self.config.ai_provider == 'grok':
            prompt_text = self._get_grok_prompt_template(wavespeed_model)
        else:
            prompt_text = self._get_prompt_template(wavespeed_model)
        
        if self.config.ai_provider == 'gemini':
            return self._generate_with_gemini(prompt_text, ref_images, sample_image)
        elif self.config.ai_provider == 'openai':
            return self._generate_with_openai(prompt_text, ref_images, sample_image)
        elif self.config.ai_provider == 'grok':
            return self._generate_with_grok(prompt_text, ref_images, sample_image)
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {self.config.ai_provider}")
    
    def _get_prompt_template(self, wavespeed_model: str = '') -> str:
        """Детальный промпт, адаптированный под выбранную модель Wavespeed"""
        
        # Определяем модель и создаем соответствующий промпт
        model_name = ""
        model_version = ""
        
        if 'seedream-v4.5' in wavespeed_model.lower() or 'seedream-v4.5' in wavespeed_model:
            model_name = "Seedream v4.5 Edit"
            model_version = "4.5"
        elif 'seedream-v4' in wavespeed_model.lower() and 'v4.5' not in wavespeed_model.lower():
            model_name = "Seedream v4 Edit"
            model_version = "4.0"
        elif 'nano-banana' in wavespeed_model.lower() or 'nano-banana-pro' in wavespeed_model.lower():
            model_name = "Nano Banana Pro"
            model_version = "Pro"
        else:
            # По умолчанию используем Seedream 4.0
            model_name = "Seedream v4.0"
            model_version = "4.0"
        
        return f"""You are an expert prompt engineer specializing in the {model_name} AI model. You create complete, detailed, and technically precise image generation prompts. Primary Directive: Your task is to analyze Reference Image 3 (a complete scene) and generate a single, comprehensive prompt for {model_name}. This prompt will instruct the model on how to use a total of three reference images. Critical Context (Non-negotiable): {model_name} will always receive 3 reference images in this specific order: Images 1 & 2: Provide the subject's complete face structure, facial features, and identity. Image 3: The complete scene reference (this is the image you will be given to analyze). Your analysis must focus exclusively on Image 3. Your generated prompt must correctly instruct {model_name} on this specific 3-image workflow. Your Generation Task: You will be given Image 3. You will analyze Image 3 ONLY. You will output ONLY the complete, formatted prompt for {model_name}. Do not add any conversational preamble, explanation, or text outside the specified format. Mandatory Output Format (Strict Template): Use the first two reference images for the subject's complete face, features, and identity. Use reference image 3 as the complete reference for all other elements: clothing, pose, action, body type, scene composition, background environment, lighting, and overall atmosphere. Subject details: [Describe the subject's clothing in exhaustive detail: every visible garment (e.g., shirt, jacket, trousers, dress), accessories (e.g., hat, scarf, belt, bag), jewelry (e.g., necklace, earrings, rings, watch), and footwear. Specify colors, patterns, textures (e.g., denim, silk, wool, leather), cuts (e.g., loose-fitting, tailored), and styles (e.g., formal, casual, athletic)]. [Describe the exact pose: sitting, standing, leaning. Detail the position of the torso, arms (e.g., folded, extended, one hand in pocket), legs (e.g., crossed, straight), and head (e.g., tilted, looking forward)]. [Describe the subject's action or gesture (e.g., holding a cup, pointing, walking, reading) and overall body language. Describe the facial expression type (e.g., a wide smile, a serious expression, a thoughtful look, a laugh) but NOT the features.] The scene: [Describe the location type (e.g., a city street, a living room, a forest, an office)]. The environment features [describe all significant background and foreground elements: architectural details (e.g., buildings, windows, walls), furniture (e.g., chairs, tables, lamps), props (e.g., books, plants, cars), and natural elements (e.g., trees, mountains, water)]. The setting is [describe the spatial layout, e.g., "indoors in a cluttered studio," "outdoors on a crowded beach"]. Lighting: [Describe the lighting in technical detail: identify the primary light source(s) (e.g., sun, studio softbox, window, lamp), its direction (e.g., side-lit, backlit, overhead, three-point lighting), its quality (e.g., hard, soft, diffused), and the resulting shadows (e.g., long and soft, sharp and deep). Note the time of day (e.g., golden hour, midday, night) and the overall color temperature (e.g., warm, cool, neutral).] Camera: [Describe the camera's properties: the angle (e.g., eye-level, low-angle, high-angle, dutch angle), the shot type (e.g., full-body shot, medium shot, cowboy shot), the depth of field (e.g., shallow with heavy bokeh, deep with everything in focus), and the overall composition (e.g., rule of thirds, centered, leading lines).] Atmosphere: [Describe the mood or ambiance of the scene (e.g., serene, chaotic, melancholic, energetic, professional, mysterious). If outdoors, note weather conditions (e.g., sunny, overcast, rainy, foggy) or environmental effects (e.g., lens flare, mist).] Colors and textures: [Describe the dominant color palette of the entire image (e.g., monochrome with a blue tint, vibrant analogous colors, muted complementary colors). Highlight key materials and their surface textures (e.g., smooth glass, rough brick, shiny metal, matte fabric, glossy paint).] Technical quality: [Describe the image's aesthetic and technical style, e.g., high-resolution, photorealistic, sharp focus, professional studio photography, cinematic, 35mm film grain, editorial fashion shot, candid.] CRITICAL RULES (ABSOLUTE): DO use generic terms: "this person," "the subject," "the individual." DO be extremely detailed about clothing, accessories, pose, and background elements. These are your primary focus. DO describe the type of facial expression (e.g., smiling, frowning, pensive) as this is part of the "pose" and "action." NEVER describe: hair color, hair style, eye color, facial features, skin tone, ethnic features Be extremely detailed about clothing and accessories Be precise about pose and body position Focus on EVERYTHING visible except facial/hair features Output ONLY the formatted prompt, nothing else."""
    
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
    
    def _generate_with_grok(self, prompt_text: str, ref_images: List[bytes], sample_image: bytes) -> str:
        """Генерация промпта через Grok (xAI)"""
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
        
        # Grok использует те же параметры что и OpenAI
        model = self.config.grok_model
        response_params = {
            'model': model,
            'messages': messages
        }
        
        # Grok модели поддерживают max_completion_tokens
        if 'grok' in model.lower():
            response_params['max_completion_tokens'] = 35000
        else:
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
                    print(f"   ⚠️  Внимание: Grok вернул пустую строку для промпта. Модель: {model}")
                    print(f"   Finish reason: {finish_reason}")
                    return ""
            else:
                print(f"   ⚠️  Внимание: Grok вернул None для message.content. Модель: {model}")
                print(f"   Finish reason: {finish_reason}")
                print(f"   Message type: {type(message)}")
                print(f"   Message attributes: {[attr for attr in dir(message) if not attr.startswith('_')]}")
                return ""
        else:
            print(f"   ⚠️  Ошибка: Grok не вернул choices для промпта. Модель: {model}")
            return ""

