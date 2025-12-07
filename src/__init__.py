"""
Makenanalog - Dataset Creation Bulk
Модульная структура для создания датасетов LoRA
"""

from .config import Config
from .file_manager import LocalFileManager
from .prompt_generator import PromptGenerator
from .image_generator import ImageGenerator
from .caption_generator import CaptionGenerator
from .dataset_creator import DatasetCreator
from .interactive_menu import interactive_menu, select_or_create_profile, save_profile_menu
from .utils import select_language
from .updater import Updater

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
    'Updater',
]

__version__ = '1.0.0'

