"""Вспомогательные функции"""

import os

try:
    from i18n import set_language
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    def set_language(lang):
        return True


def select_language():
    """Выбор языка интерфейса"""
    if not I18N_AVAILABLE:
        return
    
    # Пытаемся загрузить язык из config.json
    try:
        if os.path.exists('config.json'):
            import json
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

