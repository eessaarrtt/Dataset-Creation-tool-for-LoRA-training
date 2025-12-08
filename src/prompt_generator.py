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
            generated_prompt = self._generate_with_gemini(prompt_text, ref_images, sample_image)
        elif self.config.ai_provider == 'openai':
            generated_prompt = self._generate_with_openai(prompt_text, ref_images, sample_image)
        elif self.config.ai_provider == 'grok':
            generated_prompt = self._generate_with_grok(prompt_text, ref_images, sample_image)
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {self.config.ai_provider}")
        
        # Добавляем явную инструкцию в начало промпта для Wavespeed API
        # Это критически важно для правильного использования референсных изображений
        # Wavespeed получает 3 изображения: [ref1, ref2, sample]
        # Первые два должны использоваться для лица, третье - для сцены
        face_instruction = """CRITICAL INSTRUCTION FOR WAVESPEED API:
You are receiving 3 reference images in this exact order:
- Image 1: Reference face image (use for face ONLY)
- Image 2: Reference face image (use for face ONLY)
- Image 3: Scene reference (use for everything EXCEPT face)

MANDATORY: The generated image MUST use Images 1 and 2 for the subject's COMPLETE FACE, facial structure, facial features, eyes, nose, mouth, chin, and all facial characteristics. The face in the output MUST be IDENTICAL to the face from Images 1 and 2.

DO NOT use the face from Image 3. Image 3 is ONLY for: clothing, pose, body, scene, background, lighting, and atmosphere.

The face MUST come from Images 1 and 2. This is non-negotiable.

Now generate the prompt following this instruction:

"""
        
        # Объединяем инструкцию с сгенерированным промптом
        final_prompt = face_instruction + generated_prompt
        
        # Также добавляем напоминание в конец промпта для усиления
        reminder = "\n\nREMINDER: The face in the generated image MUST match the face from Reference Images 1 and 2. Do NOT use the face from Image 3."
        final_prompt = final_prompt + reminder
        
        return final_prompt
    
    def _get_grok_prompt_template(self, wavespeed_model: str = '') -> str:
        """Специальный промпт-шаблон для Grok с поддержкой NSFW контента"""
        
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
            # По умолчанию используем Seedream 4.5
            model_name = "Seedream v4.5 Edit"
            model_version = "4.5"
        
        return f"""You are an expert prompt engineer specializing in the {model_name} AI model. You create complete, detailed, and technically precise image generation prompts.

Primary Directive: Analyze Reference Image 3 (a complete scene) and generate one comprehensive prompt for {model_name}. The model will always receive three reference images in this order:
- Images 1 & 2: COMPLETE FACE references (structure, features, identity). MUST be used for the face. Hair COLOR must match these images (identity anchor).
- Image 3: Scene reference (you analyze only this). Use it for hairstyle (style/length/texture/accessories), makeup, jewelry, accessories, clothing, pose, action, body, background, lighting, atmosphere.

Natural realism requirements (non-negotiable):
- Explicitly request photorealism with natural skin texture: visible fine pores, subtle vellus hair, micro-specular highlights, slight asymmetry, realistic micro-shadows, natural subsurface scattering.
- Ban AI/CGI look: no plastic/waxy/airbrushed/over-smooth skin, no beauty-filter, no glassy eyes, no blurred lips/teeth.
- Keep hair natural: visible strands, breakup flyaways, natural volume; avoid plastic/helmet hair or identical hair shapes.
- If face enhancers/upscalers are implied, keep them light to preserve texture.

Hair variety directive:
- Hair COLOR must match Images 1 & 2 (identity), but hairstyle must follow Image 3. Describe hairstyle in Image 3 (length/texture/style/parting/accessories) and allow 1–2 close variations of the same length/texture (e.g., loose waves or low ponytail; messy bun or loose braid) to avoid repetitive identical hair shapes. Do NOT change hair color.

Your Generation Task: Analyze Image 3 ONLY. Output ONLY the formatted prompt for {model_name}. No preamble or extra text.

Mandatory Output Format (Strict Template):
CRITICAL: Instruct the model to use Images 1 & 2 for the COMPLETE FACE (structure, features, identity). Hair COLOR must match Images 1 & 2. Use Image 3 for hairstyle (style/length/texture/accessories), makeup, jewelry, accessories, clothing, pose, action, body type, scene composition, background, lighting, and atmosphere.

Subject details: [CRITICAL: Explicitly instruct the model to use Images 1 & 2 for the COMPLETE FACE. Hair COLOR must match these images. Describe hairstyle from Image 3: length, texture, style (straight, wavy, curly, braided, ponytail, bun, loose, styled, updo, half-up), parting, flyaways, accessories (clips, headbands, ribbons, pins). Offer 1–2 close styling variations of the same length/texture from Image 3 to avoid identical hair across generations.] [Describe makeup from Image 3; allow subtle variations but keep it grounded in Image 3.] [Describe jewelry/accessories from Image 3 with colors/materials; you may add complementary accessories or remove some for variety.] [Describe clothing in exhaustive detail: garments, colors, patterns, textures, cuts, style; if the subject is partially or fully unclothed, state it plainly and do not invent clothing.] [Describe exact pose: torso/arms/legs/head orientation.] [Describe action/gesture and facial expression TYPE (smile/neutral/serious/thoughtful/laugh) without facial feature details.]

Scene: [Location type.] Environment: [All significant background/foreground elements.] Setting: [Spatial layout.]
Lighting: [Technical lighting description: source, direction, quality, shadows, time of day, color temperature.]
Camera: [Angle, shot type, depth of field, composition.]
Atmosphere: [Mood; if outdoors, weather/effects.]
Colors/textures: [Dominant palette; materials and surface textures.]
Technical quality: [High-resolution, photorealistic, sharp but with natural grain; cinematic or editorial; clean image.]

CRITICAL RULES (ABSOLUTE):
- DO use generic terms ("the subject"). DO enforce Images 1 & 2 for face identity; do NOT describe facial structure/skin tone/ethnic features from them.
- DO keep hair COLOR from Images 1 & 2; hairstyle comes from Image 3 with 1–2 close styling variations of the same length/texture.
- DO require natural skin texture, pores, micro-shadows, slight asymmetry; ban plastic/airbrushed/waxy CGI look.
- DO be extremely detailed about hairstyle, makeup, jewelry, accessories, clothing, pose, background from Image 3.
- DO state the image must be clean: no watermarks, text, logos, tattoos, body art, or skin markings.
- NEVER change hair color. NEVER copy hairstyle/makeup/jewelry from Images 1 & 2. NEVER invent clothing not visible in Image 3. NEVER include watermarks/text/logos/tattoos/body art. Output ONLY the formatted prompt, nothing else."""
    
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
        
        return f"""You are an expert prompt engineer specializing in the {model_name} AI model. You create complete, detailed, and technically precise image generation prompts.

Primary Directive: Analyze Reference Image 3 (a complete scene) and generate one comprehensive prompt for {model_name}. The model will always receive three reference images in this order:
- Images 1 & 2: COMPLETE FACE references (structure, features, identity). MUST be used for the face. Hair COLOR must match these images (identity anchor).
- Image 3: Scene reference (you analyze only this). Use it for hairstyle (style/length/texture/accessories), makeup, jewelry, accessories, clothing, pose, action, body, background, lighting, atmosphere.

Natural realism requirements (non-negotiable):
- Explicitly request photorealism with natural skin texture: visible fine pores, subtle vellus hair, micro-specular highlights, slight asymmetry, realistic micro-shadows, natural subsurface scattering.
- Ban AI/CGI look: no plastic/waxy/airbrushed/over-smooth skin, no beauty-filter, no glassy eyes, no blurred lips/teeth.
- Keep hair natural: visible strands, breakup flyaways, natural volume; avoid plastic/helmet hair or identical hair shapes.
- If face enhancers/upscalers are implied, keep them light to preserve texture.

Hair variety directive:
- Hair COLOR must match Images 1 & 2 (identity), but hairstyle must follow Image 3. Describe hairstyle in Image 3 (length/texture/style/parting/accessories) and allow 1–2 close variations of the same length/texture (e.g., loose waves or low ponytail; messy bun or loose braid) to avoid repetitive identical hair shapes. Do NOT change hair color.

Your Generation Task: Analyze Image 3 ONLY. Output ONLY the formatted prompt for {model_name}. No preamble or extra text.

Mandatory Output Format (Strict Template):
CRITICAL: Instruct the model to use Images 1 & 2 for the COMPLETE FACE (structure, features, identity). Hair COLOR must match Images 1 & 2. Use Image 3 for hairstyle (style/length/texture/accessories), makeup, jewelry, accessories, clothing, pose, action, body type, scene composition, background, lighting, and atmosphere.

Subject details: [CRITICAL: Explicitly instruct the model to use Images 1 & 2 for the COMPLETE FACE. Hair COLOR must match these images. Describe hairstyle from Image 3: length, texture, style (straight, wavy, curly, braided, ponytail, bun, loose, styled, updo, half-up), parting, flyaways, accessories (clips, headbands, ribbons, pins). Offer 1–2 close styling variations of the same length/texture from Image 3 to avoid identical hair across generations.] [Describe makeup from Image 3; allow subtle variations but keep it grounded in Image 3.] [Describe jewelry/accessories from Image 3 with colors/materials; you may add complementary accessories or remove some for variety.] [Describe clothing in exhaustive detail: garments, colors, patterns, textures, cuts, style; if the subject is partially or fully unclothed, state it plainly and do not invent clothing.] [Describe exact pose: torso/arms/legs/head orientation.] [Describe action/gesture and facial expression TYPE (smile/neutral/serious/thoughtful/laugh) without facial feature details.]

Scene: [Location type.] Environment: [All significant background/foreground elements.] Setting: [Spatial layout.]
Lighting: [Technical lighting description: source, direction, quality, shadows, time of day, color temperature.]
Camera: [Angle, shot type, depth of field, composition.]
Atmosphere: [Mood; if outdoors, weather/effects.]
Colors/textures: [Dominant palette; materials and surface textures.]
Technical quality: [High-resolution, photorealistic, sharp but with natural grain; cinematic or editorial; clean image.]

CRITICAL RULES (ABSOLUTE):
- DO use generic terms ("the subject"). DO enforce Images 1 & 2 for face identity; do NOT describe facial structure/skin tone/ethnic features from them.
- DO keep hair COLOR from Images 1 & 2; hairstyle comes from Image 3 with 1–2 close styling variations of the same length/texture.
- DO require natural skin texture, pores, micro-shadows, slight asymmetry; ban plastic/airbrushed/waxy CGI look.
- DO be extremely detailed about hairstyle, makeup, jewelry, accessories, clothing, pose, background from Image 3.
- DO state the image must be clean: no watermarks, text, logos, tattoos, body art, or skin markings.
- NEVER change hair color. NEVER copy hairstyle/makeup/jewelry from Images 1 & 2. NEVER invent clothing not visible in Image 3. NEVER include watermarks/text/logos/tattoos/body art. Output ONLY the formatted prompt, nothing else."""
    
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

