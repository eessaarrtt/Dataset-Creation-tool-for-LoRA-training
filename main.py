#!/usr/bin/env python3
"""
Dataset Creation Bulk - Python аналог Make.com workflow
Поддерживает локальное хранение, выбор между Gemini/OpenAI и Wavespeed
"""

import argparse

from src import (
    Config,
    DatasetCreator,
    interactive_menu,
    select_or_create_profile,
    save_profile_menu,
    select_language,
    Updater
)

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
        choices=['gemini', 'openai', 'grok'],
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
    parser.add_argument(
        '--update',
        action='store_true',
        help='Обновить скрипт из GitHub репозитория'
    )
    parser.add_argument(
        '--check-updates',
        action='store_true',
        help='Проверить наличие обновлений'
    )
    parser.add_argument(
        '--force-update',
        action='store_true',
        help='Принудительное обновление (сброс локальных изменений)'
    )
    parser.add_argument(
        '--auto-update-check',
        action='store_true',
        help='Автоматически проверять обновления при запуске'
    )
    
    args = parser.parse_args()
    
    # Обработка команд обновления
    if args.update or args.check_updates or args.force_update:
        i18n = get_i18n()
        updater = Updater()
        
        if args.check_updates:
            # Только проверка обновлений
            print(f"\n🔍 {i18n.t('checking_updates')}")
            updater.show_status()
            has_updates, message = updater.check_for_updates()
            print(f"\n{message}\n")
            return
        
        if args.update or args.force_update:
            # Обновление
            success, message = updater.update(force=args.force_update)
            if success:
                print(f"\n✅ {message}\n")
                print(f"💡 {i18n.t('restart_required')}\n")
            else:
                print(f"\n❌ {message}\n")
            return
    
    # Автоматическая проверка обновлений при запуске
    if args.auto_update_check:
        i18n = get_i18n()
        updater = Updater()
        if updater.is_git_repo():
            print(f"\n🔍 {i18n.t('checking_updates')}")
            has_updates, message = updater.check_for_updates()
            if has_updates:
                print(f"\n📦 {message}\n")
                response = input(f"   {i18n.t('update_available_prompt')}").strip().lower()
                if response == 'y':
                    success, update_message = updater.update()
                    if success:
                        print(f"\n✅ {update_message}\n")
                        print(f"💡 {i18n.t('restart_required')}\n")
                        return
                    else:
                        print(f"\n❌ {update_message}\n")
            else:
                print(f"   ✓ {message}\n")
    
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

