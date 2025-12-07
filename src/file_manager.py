"""Управление локальными файлами вместо Dropbox"""

import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class LocalFileManager:
    """Управление локальными файлами вместо Dropbox"""
    
    @staticmethod
    def list_image_files(folder_path: str, limit: int = 10, content_type: Optional[str] = None, include_nsfw: bool = True) -> List[Dict]:
        """Список изображений в папке с поддержкой подпапок NSFW и обычного контента
        
        Args:
            folder_path: Путь к основной папке Sample Dataset
            limit: Максимальное количество файлов
            content_type: Тип контента - 'nsfw', 'normal' или None (все)
            include_nsfw: Включать ли файлы из папки nsfw/ (по умолчанию True)
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Папка не найдена: {folder_path}")
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        files = []
        
        # Если указан тип контента, ищем в соответствующей подпапке
        if content_type:
            subfolder = folder / content_type
            if subfolder.exists() and subfolder.is_dir():
                search_path = subfolder
            else:
                # Если подпапки нет, ищем в корне
                search_path = folder
        else:
            # Если тип не указан, ищем во всех подпапках и корне
            search_paths = []
            
            # Проверяем подпапки normal и nsfw (сначала обычный контент, потом NSFW)
            # Если include_nsfw=False, не добавляем папку nsfw
            for subfolder_name in ['normal']:
                subfolder = folder / subfolder_name
                if subfolder.exists() and subfolder.is_dir():
                    search_paths.append(subfolder)
            
            if include_nsfw:
                nsfw_subfolder = folder / 'nsfw'
                if nsfw_subfolder.exists() and nsfw_subfolder.is_dir():
                    search_paths.append(nsfw_subfolder)
            
            # Также добавляем корневую папку для обратной совместимости
            # (если файлы еще не перемещены в подпапки)
            search_paths.append(folder)
            
            # Собираем файлы из всех путей
            for search_path in search_paths:
                try:
                    for file_path in search_path.iterdir():
                        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                            # Определяем тип контента по пути
                            content_type_detected = None
                            if 'nsfw' in str(file_path.parent).lower():
                                content_type_detected = 'nsfw'
                            elif 'normal' in str(file_path.parent).lower():
                                content_type_detected = 'normal'
                            
                            # Если NSFW отключен, пропускаем файлы из папки nsfw
                            if not include_nsfw and content_type_detected == 'nsfw':
                                continue
                            
                            files.append({
                                'id': str(file_path),
                                'name': file_path.name,
                                'path': str(file_path),
                                'size': file_path.stat().st_size,
                                'content_type': content_type_detected
                            })
                            if len(files) >= limit:
                                break
                except (PermissionError, OSError):
                    # Пропускаем папки, к которым нет доступа
                    continue
                
                if len(files) >= limit:
                    break
            
            return files
        
        # Поиск в конкретной папке
        for file_path in search_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                files.append({
                    'id': str(file_path),
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'content_type': content_type
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

