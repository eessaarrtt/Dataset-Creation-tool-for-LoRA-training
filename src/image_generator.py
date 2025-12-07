"""Генератор изображений через Wavespeed"""

import base64
import json
import time
from typing import List, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
        
        # Определяем, является ли модель Seedream
        is_seedream = 'seedream' in model.lower()
        
        # Для Seedream моделей используем параметр size в формате "1920*1920"
        # Минимум для Seedream: 3686400 пикселей (1920x1920)
        if is_seedream:
            # Преобразуем wavespeed_resolution (1k, 2k, 4k) в формат size
            # Используем безопасные значения, соответствующие минимуму API
            resolution_map = {
                '1k': '1920*1920',  # Минимум для Seedream (3686400 пикселей)
                '2k': '2048*2048',  # 4194304 пикселей
                '4k': '4096*4096'   # 16777216 пикселей
            }
            resolution = getattr(self.config, 'wavespeed_resolution', '1k')
            size_value = resolution_map.get(resolution, '1920*1920')
            payload["size"] = size_value
        else:
            # Для других моделей (Nano Banana Pro) используем resolution
            if hasattr(self.config, 'wavespeed_resolution') and self.config.wavespeed_resolution:
                payload["resolution"] = self.config.wavespeed_resolution
        
        # Добавляем формат вывода если нужно
        if hasattr(self.config, 'wavespeed_output_format') and self.config.wavespeed_output_format:
            payload["output_format"] = self.config.wavespeed_output_format
        
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
        """Выполняет запрос к Wavespeed API с обработкой ошибок и повторными попытками"""
        i18n = get_i18n()
        
        # Настройка retry стратегии для HTTP запросов
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
        
        # Максимальное количество попыток (1 основная + 2 дополнительные = 3 всего)
        max_attempts = 3
        last_error = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Если это не первая попытка, выводим сообщение о повторной попытке
                if attempt > 1:
                    i18n = get_i18n()
                    wait_time = (attempt - 1) * 2  # Увеличиваем задержку с каждой попыткой
                    print(f"   ⏳ {i18n.t('retry_attempt', attempt=attempt, max=max_attempts)}")
                    print(f"   ⏳ {i18n.t('waiting_before_retry', seconds=wait_time)}")
                    time.sleep(wait_time)
                
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
                        # Это ошибка в ответе API, пробуем еще раз
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
                
                # Если дошли сюда, значит все успешно
                return result
                
            except requests.exceptions.Timeout as e:
                i18n = get_i18n()
                last_error = e
                error_msg = i18n.t('wavespeed_timeout_error', timeout=timeout_seconds)
                if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
                    error_msg += f"\n{i18n.t('server_response')}: {e.response.text[:200]}"
                
                # Если это последняя попытка, выбрасываем ошибку
                if attempt == max_attempts:
                    raise RuntimeError(error_msg)
                # Иначе продолжаем цикл для следующей попытки
                print(f"   ⚠️  {i18n.t('timeout_error_retry', attempt=attempt, max=max_attempts)}")
                continue
                
            except requests.exceptions.RequestException as e:
                i18n = get_i18n()
                last_error = e
                error_msg = i18n.t('wavespeed_request_error', error=str(e))
                if hasattr(e, 'response') and e.response is not None:
                    if hasattr(e.response, 'status_code'):
                        error_msg += f" (HTTP {e.response.status_code})"
                    if hasattr(e.response, 'text'):
                        # Ограничиваем длину ответа сервера
                        server_response = e.response.text[:500]
                        error_msg += f"\n{i18n.t('server_response')}: {server_response}"
                
                # Если это последняя попытка, выбрасываем ошибку
                if attempt == max_attempts:
                    raise RuntimeError(error_msg)
                # Иначе продолжаем цикл для следующей попытки
                print(f"   ⚠️  {i18n.t('request_error_retry', attempt=attempt, max=max_attempts)}")
                continue
                
            except (RuntimeError, ValueError) as e:
                i18n = get_i18n()
                last_error = e
                error_msg = str(e)
                
                # Если это последняя попытка, выбрасываем ошибку
                if attempt == max_attempts:
                    raise RuntimeError(error_msg)
                # Иначе продолжаем цикл для следующей попытки
                print(f"   ⚠️  {i18n.t('api_error_retry', attempt=attempt, max=max_attempts, error=error_msg[:100])}")
                continue
                
            except Exception as e:
                i18n = get_i18n()
                last_error = e
                error_msg = f"{i18n.t('unknown_error')}: {str(e)}"
                
                # Если это последняя попытка, выбрасываем ошибку
                if attempt == max_attempts:
                    raise RuntimeError(error_msg)
                # Иначе продолжаем цикл для следующей попытки
                print(f"   ⚠️  {i18n.t('unknown_error_retry', attempt=attempt, max=max_attempts)}")
                continue
        
        # Если дошли сюда (не должно произойти, но на всякий случай)
        if last_error:
            raise RuntimeError(f"{i18n.t('all_attempts_failed')}: {str(last_error)}")
        else:
            raise RuntimeError(i18n.t('all_attempts_failed'))

