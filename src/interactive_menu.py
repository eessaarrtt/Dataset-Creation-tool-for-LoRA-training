#!/usr/bin/env python3
"""
Interactive menu for dataset creation configuration
"""

import os
import re
from typing import Optional

# Rich для красивого вывода и интерактивного меню
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback если rich не установлен
    class Console:
        def __init__(self):
            pass
        def print(self, *args, **kwargs):
            print(*args)
        def clear(self):
            os.system('clear' if os.name != 'nt' else 'cls')

# Inquirer для выбора стрелками
try:
    import inquirer
    INQUIRER_AVAILABLE = True
except ImportError:
    INQUIRER_AVAILABLE = False

# Импорт системы локализации
from i18n import get_i18n

# Импорт Config
from .config import Config


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
    console = Console() if RICH_AVAILABLE else Console()
    
    # Заголовок меню
    if RICH_AVAILABLE:
        console.print("\n")
        console.print(Panel.fit(
            f"🎨 {i18n.t('interactive_menu_title')}",
            style="bold cyan",
            box=box.DOUBLE
        ))
        console.print(f"\n[dim]{i18n.t('select_settings')}[/dim]\n")
    else:
        print("\n" + "="*60)
        print(f"  🎨 {i18n.t('interactive_menu_title')}")
        print("="*60)
        print(f"\n{i18n.t('select_settings')}\n")
        print("="*60)
    
    # Вопрос о NSFW контенте в самом начале
    if RICH_AVAILABLE:
        console.print(f"\n[bold magenta]🔞 Будете ли вы генерировать NSFW контент?[/bold magenta]")
        console.print(f"[dim]Если да, для NSFW контента автоматически будут выбраны: Grok (промпты) и Seedream v4.5 (генерация)[/dim]\n")
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("", style="bold yellow", width=5)
        table.add_column("Вариант", style="", width=60)
        table.add_row("[1]", "Да, буду генерировать NSFW контент")
        table.add_row("[2]", "Нет, только обычный контент")
        console.print(table)
        nsfw_choice = Prompt.ask(f"\n   [bold]Ваш выбор[/bold]", choices=["1", "2", ""], default="", show_choices=False).strip()
    else:
        print("\n🔞 Будете ли вы генерировать NSFW контент?")
        print("Если да, для NSFW контента автоматически будут выбраны: Grok (промпты) и Seedream v4.5 (генерация)\n")
        print("   [1] Да, буду генерировать NSFW контент")
        print("   [2] Нет, только обычный контент")
        nsfw_choice = input("\n   Ваш выбор (1/2 или Enter): ").strip()
    
    # Устанавливаем флаг включения NSFW
    config.nsfw_enabled = (nsfw_choice == '1')
    
    # Автоматическая настройка для NSFW, если выбрано "Да"
    if nsfw_choice == '1':
        config.ai_provider_nsfw = 'grok'
        config.grok_model_nsfw = 'grok-4-1-fast-reasoning'
        # Устанавливаем Wavespeed модель для NSFW (будет использована, когда image_provider будет выбран)
        config.wavespeed_model_nsfw = 'bytedance/seedream-v4.5/edit'
        config.caption_provider_nsfw = 'grok'
        config.grok_caption_model_nsfw = 'grok-4-1-fast-reasoning'
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] Для NSFW контента установлено: [bold]Grok[/bold] (промпты), [bold]Seedream v4.5[/bold] (генерация), [bold]Grok[/bold] (captions)")
        else:
            print(f"   ✓ Для NSFW контента установлено: Grok (промпты), Seedream v4.5 (генерация), Grok (captions)")
    
    # Выбор AI провайдера
    # Если NSFW выбран - это настройки для обычного контента
    # Если NSFW не выбран - это основные настройки для всего контента
    if RICH_AVAILABLE:
        if nsfw_choice == '1':
            console.print(f"\n[bold cyan]1️⃣  {i18n.t('ai_provider')} (для обычного контента):[/bold cyan]")
        else:
            console.print(f"\n[bold cyan]1️⃣  {i18n.t('ai_provider')}:[/bold cyan]")
        current_ai = config.ai_provider if config.ai_provider else i18n.t('not_selected')
        console.print(f"   [dim]{i18n.t('current_value')}: {current_ai}[/dim]")
        
        # Создаем таблицу с опциями
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Choice", style="bold yellow", width=5)
        table.add_column("Provider", style="bold", width=25)
        table.add_column("Description", style="", width=50)
        
        table.add_row(
            "[bold yellow][1][/bold yellow]",
            "[bold]Gemini[/bold]",
            f"[green]✓[/green] {i18n.t('gemini_description_1')} | [green]✓[/green] {i18n.t('gemini_description_2')}"
        )
        table.add_row(
            "[bold yellow][2][/bold yellow]",
            "[bold]OpenAI[/bold]",
            f"[green]✓[/green] {i18n.t('openai_description_1')} | [green]✓[/green] {i18n.t('openai_description_2')}"
        )
        table.add_row(
            "[bold yellow][3][/bold yellow]",
            "[bold]Grok[/bold]",
            f"[green]✓[/green] {i18n.t('grok_description_1')} | [green]✓[/green] {i18n.t('grok_description_7')}"
        )
        console.print(table)
        
        choice = Prompt.ask(
            f"\n   [bold]{i18n.t('your_choice')}[/bold]",
            choices=["1", "2", "3", ""],
            default="",
            show_choices=False
        ).strip()
    else:
        print(f"\n1️⃣  {i18n.t('ai_provider')}:")
        current_ai = config.ai_provider if config.ai_provider else i18n.t('not_selected')
        print(f"   {i18n.t('current_value')}: {current_ai}")
        print(f"\n   [1] Gemini (Google Gemini 2.5 Flash)")
        print(f"       ✓ {i18n.t('gemini_description_1')}")
        print(f"       ✓ {i18n.t('gemini_description_2')}")
        print(f"       ✓ {i18n.t('gemini_description_3')}")
        print(f"       ✓ {i18n.t('gemini_description_4')}")
        print(f"       ⚠️  {i18n.t('gemini_description_5')}")
        print(f"       💡 {i18n.t('gemini_description_6')}")
        print(f"\n   [2] OpenAI (GPT-5.1)")
        print(f"       ✓ {i18n.t('openai_description_1')}")
        print(f"       ✓ {i18n.t('openai_description_2')}")
        print(f"       ✓ {i18n.t('openai_description_3')}")
        print(f"       ✓ {i18n.t('openai_description_4')}")
        print(f"       ✓ {i18n.t('openai_description_5')}")
        print(f"       ⚠️  {i18n.t('openai_description_6')}")
        print(f"       💡 {i18n.t('openai_description_7')}")
        print(f"\n   [3] Grok (xAI Grok 4.1 Fast)")
        print(f"       ✓ {i18n.t('grok_description_1')}")
        print(f"       ✓ {i18n.t('grok_description_2')}")
        print(f"       ✓ {i18n.t('grok_description_3')}")
        print(f"       ✓ {i18n.t('grok_description_4')}")
        print(f"       ⚠️  {i18n.t('grok_description_5')}")
        print(f"       💡 {i18n.t('grok_description_6')}")
        print(f"       🔥 {i18n.t('grok_description_7')}")
        choice = input(f"\n   {i18n.t('your_choice')} (1/2/3 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
    if choice == '1':
        config.ai_provider = 'gemini'
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]Gemini[/bold]")
        else:
            print(f"   ✓ {i18n.t('selected')}: Gemini")
    elif choice == '2':
        config.ai_provider = 'openai'
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]OpenAI[/bold]")
        else:
            print(f"   ✓ {i18n.t('selected')}: OpenAI")
    elif choice == '3':
        config.ai_provider = 'grok'
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]Grok[/bold]")
        else:
            print(f"   ✓ {i18n.t('selected')}: Grok")
    else:
        if config.ai_provider:
            if RICH_AVAILABLE:
                console.print(f"   [dim]→ {i18n.t('using_value')}: {config.ai_provider}[/dim]")
            else:
                print(f"   → {i18n.t('using_value')}: {config.ai_provider}")
        else:
            if RICH_AVAILABLE:
                console.print(f"   [yellow]⚠️  {i18n.t('ai_provider')} {i18n.t('not_selected')}! {i18n.t('select_option')}.[/yellow]")
            else:
                print(f"   ⚠️  {i18n.t('ai_provider')} {i18n.t('not_selected')}! {i18n.t('select_option')}.")
            # Повторяем запрос если не выбран
            while not config.ai_provider:
                if RICH_AVAILABLE:
                    choice = Prompt.ask(
                        f"   [bold]{i18n.t('your_choice')}[/bold]",
                        choices=["1", "2", "3"],
                        default="1"
                    ).strip()
                else:
                    choice = input(f"   {i18n.t('your_choice')} (1/2/3, {i18n.t('must_select')}): ").strip()
                if choice == '1':
                    config.ai_provider = 'gemini'
                    if RICH_AVAILABLE:
                        console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]Gemini[/bold]")
                    else:
                        print(f"   ✓ {i18n.t('selected')}: Gemini")
                elif choice == '2':
                    config.ai_provider = 'openai'
                    if RICH_AVAILABLE:
                        console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]OpenAI[/bold]")
                    else:
                        print(f"   ✓ {i18n.t('selected')}: OpenAI")
                elif choice == '3':
                    config.ai_provider = 'grok'
                    if RICH_AVAILABLE:
                        console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]Grok[/bold]")
                    else:
                        print(f"   ✓ {i18n.t('selected')}: Grok")
                else:
                    if RICH_AVAILABLE:
                        console.print(f"   [yellow]⚠️  {i18n.t('please_select_1_2_or_3')}[/yellow]")
                    else:
                        print(f"   ⚠️  {i18n.t('please_select_1_2_or_3')}")
    
    if RICH_AVAILABLE:
        console.print("\n[dim]" + "-"*60 + "[/dim]")
    else:
        print("\n" + "-"*60)
    
    # Выбор шаблона промпта
    if RICH_AVAILABLE:
        console.print(f"\n[bold cyan]2️⃣  {i18n.t('processing_mode')}:[/bold cyan]")
        current_template = config.prompt_template if hasattr(config, 'prompt_template') and config.prompt_template else "bulk"
        console.print(f"   [dim]{i18n.t('current_value')}: {current_template}[/dim]")
        console.print(f"\n   [yellow]⚠️  {i18n.t('prompt_same_note')}[/yellow]")
        console.print(f"   [dim]{i18n.t('prompt_difference_note')}[/dim]\n")
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Choice", style="bold yellow", width=5)
        table.add_column("Mode", style="bold", width=30)
        table.add_column("Description", style="", width=45)
        
        table.add_row(
            "[bold yellow][1][/bold yellow]",
            "[bold]bulk[/bold]",
            f"[blue]📊[/blue] {i18n.t('bulk_mode_1')} | [green]✓[/green] {i18n.t('bulk_mode_4')}"
        )
        table.add_row(
            "[bold yellow][2][/bold yellow]",
            "[bold]detailed[/bold]",
            f"[blue]📊[/blue] {i18n.t('detailed_mode_1')} | [green]✓[/green] {i18n.t('detailed_mode_4')}"
        )
        console.print(table)
        
        # Используем inquirer для выбора стрелками, если доступен
        if INQUIRER_AVAILABLE:
            questions = [
                inquirer.List(
                    'choice',
                    message=f"{i18n.t('your_choice')}",
                    choices=[
                        (f"{i18n.t('bulk_mode_title')} - {i18n.t('bulk_mode_1')}", '1'),
                        (f"{i18n.t('detailed_mode_title')} - {i18n.t('detailed_mode_1')}", '2'),
                        (f"{i18n.t('press_enter_to_skip')}", '')
                    ],
                    default='' if config.prompt_template else None
                )
            ]
            answers = inquirer.prompt(questions)
            choice = answers['choice'] if answers else ''
        else:
            choice = Prompt.ask(
                f"\n   [bold]{i18n.t('your_choice')}[/bold]",
                choices=["1", "2", ""],
                default="",
                show_choices=False
            ).strip()
    else:
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
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]bulk[/bold]")
        else:
            print(f"   ✓ {i18n.t('selected')}: bulk")
    elif choice == '2':
        config.prompt_template = 'detailed'
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]detailed[/bold]")
        else:
            print(f"   ✓ {i18n.t('selected')}: detailed")
    else:
        if RICH_AVAILABLE:
            console.print(f"   [dim]→ {i18n.t('using_value')} из config: {config.prompt_template}[/dim]")
        else:
            print(f"   → {i18n.t('using_value')} из config: {config.prompt_template}")
    
    if RICH_AVAILABLE:
        console.print("\n[dim]" + "-"*60 + "[/dim]")
    else:
        print("\n" + "-"*60)
    
    # Выбор провайдера генерации
    # Если NSFW выбран - это настройки для обычного контента
    if RICH_AVAILABLE:
        if nsfw_choice == '1':
            console.print(f"\n[bold cyan]3️⃣  {i18n.t('image_generation_provider')} (для обычного контента):[/bold cyan]")
        else:
            console.print(f"\n[bold cyan]3️⃣  {i18n.t('image_generation_provider')}:[/bold cyan]")
        current_provider = config.image_provider if config.image_provider else i18n.t('not_selected')
        console.print(f"   [dim]{i18n.t('current_value')}: {current_provider}[/dim]")
        console.print(f"\n   [bold yellow][1][/bold yellow] [bold]Wavespeed[/bold]")
        console.print(f"       [green]✓[/green] {i18n.t('wavespeed_description_1')}")
        console.print(f"       [green]✓[/green] {i18n.t('wavespeed_description_2')}")
        console.print(f"       [green]✓[/green] {i18n.t('wavespeed_description_3')}")
        console.print(f"       [green]✓[/green] {i18n.t('wavespeed_description_4')}")
        console.print(f"       [green]✓[/green] {i18n.t('wavespeed_description_5')}")
        console.print(f"       [blue]💡[/blue] {i18n.t('wavespeed_description_6')}")
        # Используем inquirer для выбора стрелками, если доступен
        if INQUIRER_AVAILABLE:
            questions = [
                inquirer.List(
                    'choice',
                    message=f"{i18n.t('your_choice')}",
                    choices=[
                        ('Wavespeed', '1'),
                        (f"{i18n.t('press_enter_to_skip')}", '')
                    ],
                    default='' if config.image_provider else None
                )
            ]
            answers = inquirer.prompt(questions)
            choice = answers['choice'] if answers else ''
        else:
            choice = Prompt.ask(
                f"\n   [bold]{i18n.t('your_choice')}[/bold]",
                choices=["1", ""],
                default="",
                show_choices=False
            ).strip()
    else:
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
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]Wavespeed[/bold]")
        else:
            print(f"   ✓ {i18n.t('selected')}: Wavespeed")
    else:
        if config.image_provider:
            if RICH_AVAILABLE:
                console.print(f"   [dim]→ {i18n.t('using_value')}: {config.image_provider}[/dim]")
            else:
                print(f"   → {i18n.t('using_value')}: {config.image_provider}")
        else:
            if RICH_AVAILABLE:
                console.print(f"   [yellow]⚠️  {i18n.t('image_generation_provider')} {i18n.t('not_selected')}! {i18n.t('select_option')}.[/yellow]")
            else:
                print(f"   ⚠️  {i18n.t('image_generation_provider')} {i18n.t('not_selected')}! {i18n.t('select_option')}.")
            # Повторяем запрос если не выбран
            while not config.image_provider:
                if RICH_AVAILABLE:
                    choice = Prompt.ask(
                        f"   [bold]{i18n.t('your_choice')}[/bold]",
                        choices=["1"],
                        default="1"
                    ).strip()
                else:
                    choice = input(f"   {i18n.t('your_choice')} (1, {i18n.t('must_select')}): ").strip()
                if choice == '1':
                    config.image_provider = 'wavespeed'
                    if RICH_AVAILABLE:
                        console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]Wavespeed[/bold]")
                    else:
                        print(f"   ✓ {i18n.t('selected')}: Wavespeed")
                else:
                    if RICH_AVAILABLE:
                        console.print(f"   [yellow]⚠️  {i18n.t('please_select_1')}[/yellow]")
                    else:
                        print(f"   ⚠️  {i18n.t('please_select_1')}")
    
    if RICH_AVAILABLE:
        console.print("\n[dim]" + "-"*60 + "[/dim]")
    else:
        print("\n" + "-"*60)
    
    # Выбор модели Wavespeed
    # Если NSFW выбран - это настройки для обычного контента
    if config.image_provider == 'wavespeed':
        if RICH_AVAILABLE:
            console.print("\n[dim]" + "-"*60 + "[/dim]")
            if nsfw_choice == '1':
                console.print(f"\n[bold cyan]4️⃣  {i18n.t('wavespeed_model')} (для обычного контента):[/bold cyan]")
            else:
                console.print(f"\n[bold cyan]4️⃣  {i18n.t('wavespeed_model')}:[/bold cyan]")
            console.print(f"   [dim]{i18n.t('current_value')}: {config.wavespeed_model}[/dim]")
            
            # Создаем таблицу с моделями
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Choice", style="bold yellow", width=5)
            table.add_column("Model", style="bold", width=40)
            table.add_column("Key Features", style="", width=35)
            
            table.add_row(
                "[bold yellow][1][/bold yellow]",
                "[bold]google/nano-banana-pro/edit[/bold]",
                f"[green]•[/green] {i18n.t('nano_banana_1')} | [green]•[/green] {i18n.t('nano_banana_5')}"
            )
            table.add_row(
                "[bold yellow][2][/bold yellow]",
                "[bold]bytedance/seedream-v4.5/edit[/bold]",
                f"[green]•[/green] {i18n.t('seedream_v45_1')} | [green]•[/green] {i18n.t('seedream_v45_6')}"
            )
            table.add_row(
                "[bold yellow][3][/bold yellow]",
                "[bold]bytedance/seedream-v4/edit[/bold]",
                f"[green]•[/green] {i18n.t('seedream_v4_1')} | [green]•[/green] {i18n.t('seedream_v4_6')}"
            )
            table.add_row(
                "[bold yellow][4][/bold yellow]",
                "[bold]alibaba/wan-2.5/image-to-video[/bold]",
                f"[green]•[/green] {i18n.t('wan_25_1')} | [dim]⚠️ В разработке[/dim]"
            )
            table.add_row(
                "[bold yellow][5][/bold yellow]",
                "[bold]kwaivgi/kling-v2.6-pro/image-to-video[/bold]",
                f"[green]•[/green] {i18n.t('kling_v26_1')} | [dim]⚠️ В разработке[/dim]"
            )
            table.add_row(
                "[bold yellow][6][/bold yellow]",
                "[bold]kwaivgi/kling-v2.5-turbo-pro/image-to-video[/bold]",
                f"[green]•[/green] {i18n.t('kling_v25_1')} | [dim]⚠️ В разработке[/dim]"
            )
            console.print(f"\n   [bold]{i18n.t('image_to_image')}[/bold]")
            console.print(table)
            console.print(f"\n   [dim]{i18n.t('image_to_video')}[/dim]")
            console.print(f"   [dim]⚠️  Модули для video в разработке, будут доступны в следующих версиях[/dim]")
            
            # Используем inquirer для выбора стрелками, если доступен
            if INQUIRER_AVAILABLE:
                questions = [
                    inquirer.List(
                        'choice',
                        message=f"{i18n.t('your_choice')}",
                        choices=[
                            ('google/nano-banana-pro/edit', '1'),
                            ('bytedance/seedream-v4.5/edit', '2'),
                            ('bytedance/seedream-v4/edit', '3'),
                            ('alibaba/wan-2.5/image-to-video (⚠️ В разработке)', '4'),
                            ('kwaivgi/kling-v2.6-pro/image-to-video (⚠️ В разработке)', '5'),
                            ('kwaivgi/kling-v2.5-turbo-pro/image-to-video (⚠️ В разработке)', '6'),
                            (f"{i18n.t('press_enter_to_skip')}", '')
                        ],
                        default='' if config.wavespeed_model else None
                    )
                ]
                answers = inquirer.prompt(questions)
                choice = answers['choice'] if answers else ''
            else:
                choice = Prompt.ask(
                    f"\n   [bold]{i18n.t('your_choice')}[/bold]",
                    choices=["1", "2", "3", "4", "5", "6", ""],
                    default="",
                    show_choices=False
                ).strip()
        else:
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
            print(f"\n      [2] bytedance/seedream-v4.5/edit")
            print(f"         • {i18n.t('seedream_v45_1')}")
            print(f"         • {i18n.t('seedream_v45_2')}")
            print(f"         • {i18n.t('seedream_v45_3')}")
            print(f"         • {i18n.t('seedream_v45_4')}")
            print(f"         • {i18n.t('seedream_v45_5')}")
            print(f"         • {i18n.t('seedream_v45_6')}")
            print(f"         • {i18n.t('seedream_v45_7')}")
            print(f"\n      [3] bytedance/seedream-v4/edit")
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
            '2': 'bytedance/seedream-v4.5/edit',
            '3': 'bytedance/seedream-v4/edit',
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
            if RICH_AVAILABLE:
                console.print("\n[dim]" + "-"*60 + "[/dim]")
                console.print(f"\n[bold cyan]5️⃣  {i18n.t('wavespeed_resolution')}:[/bold cyan]")
                console.print(f"   [dim]{i18n.t('current_value')}: {config.wavespeed_resolution}[/dim]")
            else:
                print("\n" + "-"*60)
                print(f"\n5️⃣  {i18n.t('wavespeed_resolution')}:")
                print(f"   {i18n.t('current_value')}: {config.wavespeed_resolution}")
            
            if INQUIRER_AVAILABLE:
                questions = [
                    inquirer.List(
                        'choice',
                        message=f"{i18n.t('your_choice')}",
                        choices=[
                            ('1k (1920×1920) - Быстрая генерация', '1'),
                            ('2k (2048×2048) - Баланс качества и скорости', '2'),
                            ('4k (4096×4096) - Максимальное качество', '3'),
                            (f"{i18n.t('press_enter_to_skip')}", '')
                        ],
                        default='' if config.wavespeed_resolution else None
                    )
                ]
                answers = inquirer.prompt(questions)
                choice = answers['choice'] if answers else ''
            else:
                if RICH_AVAILABLE:
                    console.print("\n   [bold yellow][1][/bold yellow] [bold]1k[/bold] (1920×1920)")
                    console.print(f"       [green]✓[/green] {i18n.t('resolution_1k_1')}")
                    console.print(f"       [green]✓[/green] {i18n.t('resolution_1k_2')}")
                    console.print(f"       [yellow]⚠️[/yellow]  {i18n.t('resolution_1k_3')}")
                    console.print(f"       [blue]💡[/blue] {i18n.t('resolution_1k_4')}")
                    console.print("\n   [bold yellow][2][/bold yellow] [bold]2k[/bold] (2048×2048)")
                    console.print(f"       [green]✓[/green] {i18n.t('resolution_2k_1')}")
                    console.print(f"       [green]✓[/green] {i18n.t('resolution_2k_2')}")
                    console.print(f"       [blue]💡[/blue] {i18n.t('resolution_2k_3')}")
                    console.print("\n   [bold yellow][3][/bold yellow] [bold]4k[/bold] (4096×4096)")
                    console.print(f"       [green]✓[/green] {i18n.t('resolution_4k_1')}")
                    console.print(f"       [green]✓[/green] {i18n.t('resolution_4k_2')}")
                    console.print(f"       [yellow]⚠️[/yellow]  {i18n.t('resolution_4k_3')}")
                    console.print(f"       [blue]💡[/blue] {i18n.t('resolution_4k_4')}")
                    choice = Prompt.ask(
                        f"\n   [bold]{i18n.t('your_choice')}[/bold]",
                        choices=["1", "2", "3", ""],
                        default="",
                        show_choices=False
                    ).strip()
                else:
                    print("\n   [1] 1k (1920×1920 или аналогичное)")
                    print(f"       ✓ {i18n.t('resolution_1k_1')}")
                    print(f"       ✓ {i18n.t('resolution_1k_2')}")
                    print(f"       ⚠️  {i18n.t('resolution_1k_3')}")
                    print(f"       💡 {i18n.t('resolution_1k_4')}")
                    print("\n   [2] 2k (2048×2048 или аналогичное)")
                    print(f"       ✓ {i18n.t('resolution_2k_1')}")
                    print(f"       ✓ {i18n.t('resolution_2k_2')}")
                    print(f"       💡 {i18n.t('resolution_2k_3')}")
                    print("\n   [3] 4k (4096×4096 или аналогичное)")
                    print(f"       ✓ {i18n.t('resolution_4k_1')}")
                    print(f"       ✓ {i18n.t('resolution_4k_2')}")
                    print(f"       ⚠️  {i18n.t('resolution_4k_3')}")
                    print(f"       💡 {i18n.t('resolution_4k_4')}")
                    choice = input(f"\n   {i18n.t('your_choice')} (1-3 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
            
            resolutions = {'1': '1k', '2': '2k', '3': '4k'}
            if choice in resolutions:
                config.wavespeed_resolution = resolutions[choice]
                if RICH_AVAILABLE:
                    console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]{config.wavespeed_resolution}[/bold]")
                else:
                    print(f"   ✓ {i18n.t('selected')}: {config.wavespeed_resolution}")
            else:
                if RICH_AVAILABLE:
                    console.print(f"   [dim]→ {i18n.t('using_value')} из config: {config.wavespeed_resolution}[/dim]")
                else:
                    print(f"   → {i18n.t('using_value')} из config: {config.wavespeed_resolution}")
    
    if RICH_AVAILABLE:
        console.print("\n[dim]" + "-"*60 + "[/dim]")
    else:
        print("\n" + "-"*60)
    
    # Настройки для генерации captions (LoRA)
    # Если NSFW выбран - это настройки для обычного контента
    if RICH_AVAILABLE:
        if nsfw_choice == '1':
            console.print(f"\n[bold cyan]6️⃣  {i18n.t('caption_generation')} (для обычного контента):[/bold cyan]")
        else:
            console.print(f"\n[bold cyan]6️⃣  {i18n.t('caption_generation')}:[/bold cyan]")
        current_generate = i18n.t('yes') if config.generate_captions else i18n.t('no')
        console.print(f"   [dim]{i18n.t('current_value')}: {current_generate}[/dim]")
        console.print(f"\n   {i18n.t('caption_generation_desc')}")
    else:
        print(f"\n6️⃣  {i18n.t('caption_generation')}:")
        current_generate = i18n.t('yes') if config.generate_captions else i18n.t('no')
        print(f"   {i18n.t('current_value')}: {current_generate}")
        print(f"\n   {i18n.t('caption_generation_desc')}")
    
    if INQUIRER_AVAILABLE:
        questions = [
            inquirer.List(
                'choice',
                message=f"{i18n.t('your_choice')}",
                choices=[
                    (f"{i18n.t('caption_generation_yes')} - {i18n.t('caption_yes_1')}", '1'),
                    (f"{i18n.t('caption_generation_no')} - {i18n.t('caption_no_1')}", '2'),
                    (f"{i18n.t('press_enter_to_skip')}", '')
                ],
                default='' if config.generate_captions else None
            )
        ]
        answers = inquirer.prompt(questions)
        choice = answers['choice'] if answers else ''
    else:
        if RICH_AVAILABLE:
            console.print(f"\n   [bold yellow][1][/bold yellow] [bold]{i18n.t('caption_generation_yes')}[/bold]")
            console.print(f"       [green]✓[/green] {i18n.t('caption_yes_1')}")
            console.print(f"       [green]✓[/green] {i18n.t('caption_yes_2')}")
            console.print(f"       [green]✓[/green] {i18n.t('caption_yes_3')}")
            console.print(f"       [yellow]⚠️[/yellow]  {i18n.t('caption_yes_4')}")
            console.print(f"       [yellow]⚠️[/yellow]  {i18n.t('caption_yes_5')}")
            console.print(f"       [blue]💡[/blue] {i18n.t('caption_yes_6')}")
            console.print(f"\n   [bold yellow][2][/bold yellow] [bold]{i18n.t('caption_generation_no')}[/bold]")
            console.print(f"       [green]✓[/green] {i18n.t('caption_no_1')}")
            console.print(f"       [green]✓[/green] {i18n.t('caption_no_2')}")
            console.print(f"       [blue]💡[/blue] {i18n.t('caption_no_3')}")
            choice = Prompt.ask(
                f"\n   [bold]{i18n.t('your_choice')}[/bold]",
                choices=["1", "2", ""],
                default="",
                show_choices=False
            ).strip()
        else:
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
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('caption_enabled')}")
        else:
            print(f"   ✓ {i18n.t('caption_enabled')}")
        
        if RICH_AVAILABLE:
            console.print("\n[dim]" + "-"*60 + "[/dim]")
        else:
            print("\n" + "-"*60)
        
        # Запрашиваем trigger name
        if RICH_AVAILABLE:
            console.print(f"\n[bold cyan]7️⃣  {i18n.t('trigger_name_prompt')}:[/bold cyan]")
            current_trigger = config.trigger_name if config.trigger_name else i18n.t('not_selected')
            console.print(f"   [dim]{i18n.t('current_value')}: {current_trigger}[/dim]")
            console.print(f"\n   {i18n.t('trigger_name_desc')}")
            console.print(f"   {i18n.t('trigger_name_examples')}")
            console.print(f"   [yellow]⚠️[/yellow]  {i18n.t('trigger_name_warning')}")
            trigger_input = Prompt.ask(
                f"\n   [bold]{i18n.t('enter')} trigger name[/bold]",
                default=config.trigger_name if config.trigger_name else ""
            ).strip()
        else:
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
            if RICH_AVAILABLE:
                console.print(f"   [green]✓[/green] {i18n.t('trigger_name_set', name=trigger_name)}")
            else:
                print(f"   ✓ {i18n.t('trigger_name_set', name=trigger_name)}")
        else:
            if config.trigger_name:
                if RICH_AVAILABLE:
                    console.print(f"   [dim]→ {i18n.t('using_value')} из config: {config.trigger_name}[/dim]")
                else:
                    print(f"   → {i18n.t('using_value')} из config: {config.trigger_name}")
            else:
                if RICH_AVAILABLE:
                    console.print(f"   [yellow]⚠️  {i18n.t('trigger_name_not_set')}[/yellow]")
                else:
                    print(f"   ⚠️  {i18n.t('trigger_name_not_set')}")
                config.generate_captions = False
        
        # Выбор провайдера для генерации captions
        if config.generate_captions:
            if RICH_AVAILABLE:
                console.print("\n[dim]" + "-"*60 + "[/dim]")
                console.print(f"\n[bold cyan]8️⃣  {i18n.t('caption_provider')}:[/bold cyan]")
                current_provider = getattr(config, 'caption_provider', 'openai')
                console.print(f"   [dim]{i18n.t('current_value')}: {current_provider}[/dim]")
                console.print(f"\n   {i18n.t('caption_provider_desc')}")
            else:
                print("\n" + "-"*60)
                print(f"\n8️⃣  {i18n.t('caption_provider')}:")
                current_provider = getattr(config, 'caption_provider', 'openai')
                print(f"   {i18n.t('current_value')}: {current_provider}")
                print(f"\n   {i18n.t('caption_provider_desc')}")
            
            if INQUIRER_AVAILABLE:
                questions = [
                    inquirer.List(
                        'choice',
                        message=f"{i18n.t('your_choice')}",
                        choices=[
                            (f"OpenAI - {i18n.t('openai_caption_desc')}", '1'),
                            (f"Grok - {i18n.t('grok_caption_desc')}", '2'),
                            (f"{i18n.t('press_enter_to_skip')}", '')
                        ],
                        default='' if getattr(config, 'caption_provider', None) else None
                    )
                ]
                answers = inquirer.prompt(questions)
                choice = answers['choice'] if answers else ''
            else:
                if RICH_AVAILABLE:
                    console.print("\n   [bold yellow][1][/bold yellow] [bold]OpenAI[/bold]")
                    console.print(f"       [green]✓[/green] {i18n.t('openai_caption_desc')}")
                    console.print(f"       [yellow]⚠️[/yellow]  {i18n.t('openai_nsfw_warning')}")
                    console.print(f"\n   [bold yellow][2][/bold yellow] [bold]Grok[/bold]")
                    console.print(f"       [green]✓[/green] {i18n.t('grok_caption_desc')}")
                    console.print(f"       [green]✓[/green] {i18n.t('grok_nsfw_support')}")
                    choice = Prompt.ask(
                        f"\n   [bold]{i18n.t('your_choice')}[/bold]",
                        choices=["1", "2", ""],
                        default="",
                        show_choices=False
                    ).strip()
                else:
                    print("\n   [1] OpenAI")
                    print(f"       ✓ {i18n.t('openai_caption_desc')}")
                    print(f"       ⚠️  {i18n.t('openai_nsfw_warning')}")
                    print(f"\n   [2] Grok")
                    print(f"       ✓ {i18n.t('grok_caption_desc')}")
                    print(f"       ✓ {i18n.t('grok_nsfw_support')}")
                    choice = input(f"\n   {i18n.t('your_choice')} (1/2 {i18n.t('or')} {i18n.t('press_enter_to_skip')}): ").strip()
            
            providers = {
                '1': 'openai',
                '2': 'grok'
            }
            if choice in providers:
                config.caption_provider = providers[choice]
                if RICH_AVAILABLE:
                    console.print(f"   [green]✓[/green] {i18n.t('selected')}: [bold]{providers[choice].upper()}[/bold]")
                else:
                    print(f"   ✓ {i18n.t('selected')}: {providers[choice].upper()}")
            else:
                if hasattr(config, 'caption_provider') and config.caption_provider:
                    if RICH_AVAILABLE:
                        console.print(f"   [dim]→ {i18n.t('using_value')} из config: {config.caption_provider}[/dim]")
                    else:
                        print(f"   → {i18n.t('using_value')} из config: {config.caption_provider}")
                else:
                    config.caption_provider = 'openai'
                    if RICH_AVAILABLE:
                        console.print(f"   [dim]→ {i18n.t('using_value')} по умолчанию: openai[/dim]")
                    else:
                        print(f"   → {i18n.t('using_value')} по умолчанию: openai")
            
            # Выбор модели в зависимости от провайдера
            if RICH_AVAILABLE:
                console.print("\n[dim]" + "-"*60 + "[/dim]")
                if config.caption_provider == 'grok':
                    console.print(f"\n[bold cyan]9️⃣  {i18n.t('grok_caption_model')}:[/bold cyan]")
                    current_caption_model = getattr(config, 'grok_caption_model', None) or config.grok_model or "grok-4-1-fast-reasoning"
                else:
                    console.print(f"\n[bold cyan]9️⃣  {i18n.t('openai_caption_model')}:[/bold cyan]")
                    current_caption_model = getattr(config, 'openai_caption_model', None) or config.openai_model or "gpt-5.1"
                console.print(f"   [dim]{i18n.t('current_value')}: {current_caption_model}[/dim]")
            else:
                print("\n" + "-"*60)
                if config.caption_provider == 'grok':
                    print(f"\n9️⃣  {i18n.t('grok_caption_model')}:")
                    current_caption_model = getattr(config, 'grok_caption_model', None) or config.grok_model or "grok-4-1-fast-reasoning"
                else:
                    print(f"\n9️⃣  {i18n.t('openai_caption_model')}:")
                    current_caption_model = getattr(config, 'openai_caption_model', None) or config.openai_model or "gpt-5.1"
                print(f"   {i18n.t('current_value')}: {current_caption_model}")
            
            # Выбор модели в зависимости от провайдера
            if config.caption_provider == 'grok':
                # Для Grok используется только grok-4-1-fast-reasoning
                config.grok_caption_model = 'grok-4-1-fast-reasoning'
                if RICH_AVAILABLE:
                    console.print(f"   [dim]→ {i18n.t('using_value')} по умолчанию: {config.grok_caption_model}[/dim]")
                else:
                    print(f"   → {i18n.t('using_value')} по умолчанию: {config.grok_caption_model}")
            else:
                # Используем только gpt-5.1 для OpenAI captions
                config.openai_caption_model = 'gpt-5.1'
                if RICH_AVAILABLE:
                    console.print(f"   [dim]→ {i18n.t('using_value')} по умолчанию: {config.openai_caption_model}[/dim]")
                else:
                    print(f"   → {i18n.t('using_value')} по умолчанию: {config.openai_caption_model}")
    elif choice == '2':
        config.generate_captions = False
        if RICH_AVAILABLE:
            console.print(f"   [green]✓[/green] {i18n.t('caption_disabled')}")
        else:
            print(f"   ✓ {i18n.t('caption_disabled')}")
    else:
        if config.generate_captions:
            if RICH_AVAILABLE:
                console.print(f"   [dim]→ {i18n.t('using_value')} из config: {i18n.t('yes') if config.generate_captions else i18n.t('no')}[/dim]")
            else:
                print(f"   → {i18n.t('using_value')} из config: {i18n.t('yes') if config.generate_captions else i18n.t('no')}")
            if config.generate_captions and not config.trigger_name:
                if RICH_AVAILABLE:
                    console.print(f"   [yellow]⚠️  {i18n.t('trigger_name_warning_caption')}[/yellow]")
                else:
                    print(f"   ⚠️  {i18n.t('trigger_name_warning_caption')}")
    
    # Если NSFW выбран, сохраняем основные настройки в настройки обычного контента
    if nsfw_choice == '1':
        # Основные настройки, которые были выбраны, применяются к обычному контенту
        if config.ai_provider and not config.ai_provider_normal:
            config.ai_provider_normal = config.ai_provider
            # Устанавливаем соответствующую модель
            if config.ai_provider == 'gemini':
                config.gemini_model_normal = config.gemini_model
            elif config.ai_provider == 'openai':
                config.openai_model_normal = config.openai_model
            elif config.ai_provider == 'grok':
                config.grok_model_normal = config.grok_model
        
        if config.image_provider == 'wavespeed' and config.wavespeed_model and not config.wavespeed_model_normal:
            config.wavespeed_model_normal = config.wavespeed_model
        
        if config.generate_captions:
            caption_provider_main = getattr(config, 'caption_provider', 'openai')
            if not config.caption_provider_normal:
                config.caption_provider_normal = caption_provider_main
                if caption_provider_main == 'openai':
                    config.openai_caption_model_normal = getattr(config, 'openai_caption_model', 'gpt-5.1')
                elif caption_provider_main == 'grok':
                    config.grok_caption_model_normal = getattr(config, 'grok_caption_model', 'grok-4-1-fast-reasoning')
    
    i18n = get_i18n()
    if RICH_AVAILABLE:
        console.print("\n")
        console.print(Panel.fit(
            f"✅ {i18n.t('settings_selected')}",
            style="bold green",
            box=box.DOUBLE
        ))
        console.print(f"\n[bold]📋 {i18n.t('final_settings')}[/bold]\n")
        
        # Основные настройки
        if nsfw_choice == '1':
            console.print(f"[bold cyan]🔧 {i18n.t('normal_content_settings')}:[/bold cyan]")
        else:
            console.print(f"[bold cyan]🔧 {i18n.t('main_settings')}:[/bold cyan]")
        console.print(f"   [cyan]{i18n.t('ai_provider')}:[/cyan] [bold]{config.ai_provider}[/bold]")
        console.print(f"   [cyan]{i18n.t('prompt_template')}:[/cyan] [bold]{config.prompt_template}[/bold]")
        console.print(f"   [cyan]{i18n.t('image_generation_provider')}:[/cyan] [bold]{config.image_provider}[/bold]")
        if config.image_provider == 'wavespeed':
            console.print(f"   [cyan]{i18n.t('wavespeed_model')}:[/cyan] [bold]{config.wavespeed_model}[/bold]")
            console.print(f"   [cyan]{i18n.t('resolution_label')}:[/cyan] [bold]{config.wavespeed_resolution}[/bold]")
        if config.generate_captions:
            console.print(f"   [cyan]{i18n.t('caption_generation')}:[/cyan] [bold green]{i18n.t('yes')}[/bold green]")
            console.print(f"   [cyan]{i18n.t('trigger_name')}:[/cyan] [bold]{config.trigger_name if config.trigger_name else i18n.t('not_selected')}[/bold]")
            caption_provider = getattr(config, 'caption_provider', 'openai')
            console.print(f"   [cyan]{i18n.t('caption_provider')}:[/cyan] [bold]{caption_provider.upper()}[/bold]")
            if caption_provider == 'grok':
                caption_model = getattr(config, 'grok_caption_model', None) or config.grok_model or 'grok-4-1-fast-reasoning'
                console.print(f"   [cyan]{i18n.t('grok_caption_model')}:[/cyan] [bold]{caption_model}[/bold]")
            else:
                caption_model = getattr(config, 'openai_caption_model', None) or config.openai_model or 'gpt-5.1'
                console.print(f"   [cyan]{i18n.t('openai_caption_model')}:[/cyan] [bold]{caption_model}[/bold]")
        else:
            console.print(f"   [cyan]{i18n.t('caption_generation')}:[/cyan] [dim]{i18n.t('no')}[/dim]")
        
        # Настройки для NSFW и обычного контента (показываем только если NSFW был выбран)
        if nsfw_choice == '1':
            has_nsfw_settings = config.ai_provider_nsfw or config.wavespeed_model_nsfw or config.caption_provider_nsfw
            has_normal_settings = config.ai_provider_normal or config.wavespeed_model_normal or config.caption_provider_normal
            
            if has_nsfw_settings or has_normal_settings:
                console.print(f"\n[bold magenta]🔞 {i18n.t('nsfw_normal_content_settings')}:[/bold magenta]")
                
                # NSFW настройки
                if has_nsfw_settings:
                    console.print(f"\n   [bold magenta]📌 {i18n.t('nsfw_content')}:[/bold magenta]")
                    nsfw_ai = config.ai_provider_nsfw if config.ai_provider_nsfw else i18n.t('main_value', value=config.ai_provider)
                    console.print(f"      [cyan]{i18n.t('ai_provider_prompts')}:[/cyan] [bold]{nsfw_ai}[/bold]")
                    if config.image_provider == 'wavespeed':
                        nsfw_model = config.wavespeed_model_nsfw if config.wavespeed_model_nsfw else i18n.t('main_value', value=config.wavespeed_model)
                        console.print(f"      [cyan]{i18n.t('wavespeed_model_label')}:[/cyan] [bold]{nsfw_model}[/bold]")
                    if config.generate_captions:
                        caption_provider_main = getattr(config, 'caption_provider', 'openai')
                        nsfw_caption = config.caption_provider_nsfw if config.caption_provider_nsfw else i18n.t('main_value', value=caption_provider_main)
                        console.print(f"      [cyan]{i18n.t('provider_captions')}:[/cyan] [bold]{nsfw_caption}[/bold]")
                
                # Обычный контент настройки
                if has_normal_settings:
                    console.print(f"\n   [bold green]📌 {i18n.t('normal_content')}:[/bold green]")
                    normal_ai = config.ai_provider_normal if config.ai_provider_normal else i18n.t('main_value', value=config.ai_provider)
                    console.print(f"      [cyan]{i18n.t('ai_provider_prompts')}:[/cyan] [bold]{normal_ai}[/bold]")
                    if config.image_provider == 'wavespeed':
                        normal_model = config.wavespeed_model_normal if config.wavespeed_model_normal else i18n.t('main_value', value=config.wavespeed_model)
                        console.print(f"      [cyan]{i18n.t('wavespeed_model_label')}:[/cyan] [bold]{normal_model}[/bold]")
                    if config.generate_captions:
                        caption_provider_main = getattr(config, 'caption_provider', 'openai')
                        normal_caption = config.caption_provider_normal if config.caption_provider_normal else i18n.t('main_value', value=caption_provider_main)
                        console.print(f"      [cyan]{i18n.t('provider_captions')}:[/cyan] [bold]{normal_caption}[/bold]")
    else:
        print("\n" + "="*60)
        print(f"  ✅ {i18n.t('settings_selected')}")
        print("="*60)
        print(f"\n📋 {i18n.t('final_settings')}\n")
        
        # Основные настройки
        if nsfw_choice == '1':
            print(f"🔧 {i18n.t('normal_content_settings')}:")
        else:
            print(f"🔧 {i18n.t('main_settings')}:")
        print(f"   {i18n.t('ai_provider')}: {config.ai_provider}")
        print(f"   {i18n.t('prompt_template')}: {config.prompt_template}")
        print(f"   {i18n.t('image_generation_provider')}: {config.image_provider}")
        if config.image_provider == 'wavespeed':
            print(f"   {i18n.t('wavespeed_model')}: {config.wavespeed_model}")
            print(f"   {i18n.t('resolution_label')}: {config.wavespeed_resolution}")
        if config.generate_captions:
            print(f"   {i18n.t('caption_generation')}: {i18n.t('yes')}")
            print(f"   {i18n.t('trigger_name')}: {config.trigger_name if config.trigger_name else i18n.t('not_selected')}")
            caption_provider = getattr(config, 'caption_provider', 'openai')
            print(f"   {i18n.t('caption_provider')}: {caption_provider.upper()}")
            if caption_provider == 'grok':
                caption_model = getattr(config, 'grok_caption_model', None) or config.grok_model or 'grok-4-1-fast-reasoning'
                print(f"   {i18n.t('grok_caption_model')}: {caption_model}")
            else:
                caption_model = getattr(config, 'openai_caption_model', None) or config.openai_model or 'gpt-5.1'
                print(f"   {i18n.t('openai_caption_model')}: {caption_model}")
        else:
            print(f"   {i18n.t('caption_generation')}: {i18n.t('no')}")
        
        # Настройки для NSFW и обычного контента (показываем только если NSFW был выбран)
        if nsfw_choice == '1':
            has_nsfw_settings = config.ai_provider_nsfw or config.wavespeed_model_nsfw or config.caption_provider_nsfw
            has_normal_settings = config.ai_provider_normal or config.wavespeed_model_normal or config.caption_provider_normal
            
            if has_nsfw_settings or has_normal_settings:
                print(f"\n🔞 {i18n.t('nsfw_normal_content_settings')}:")
                
                # NSFW настройки
                if has_nsfw_settings:
                    print(f"\n   📌 {i18n.t('nsfw_content')}:")
                    nsfw_ai = config.ai_provider_nsfw if config.ai_provider_nsfw else i18n.t('main_value', value=config.ai_provider)
                    print(f"      {i18n.t('ai_provider_prompts')}: {nsfw_ai}")
                    if config.image_provider == 'wavespeed':
                        nsfw_model = config.wavespeed_model_nsfw if config.wavespeed_model_nsfw else i18n.t('main_value', value=config.wavespeed_model)
                        print(f"      {i18n.t('wavespeed_model_label')}: {nsfw_model}")
                    if config.generate_captions:
                        caption_provider_main = getattr(config, 'caption_provider', 'openai')
                        nsfw_caption = config.caption_provider_nsfw if config.caption_provider_nsfw else i18n.t('main_value', value=caption_provider_main)
                        print(f"      {i18n.t('provider_captions')}: {nsfw_caption}")
                
                # Обычный контент настройки
                if has_normal_settings:
                    print(f"\n   📌 {i18n.t('normal_content')}:")
                    normal_ai = config.ai_provider_normal if config.ai_provider_normal else i18n.t('main_value', value=config.ai_provider)
                    print(f"      {i18n.t('ai_provider_prompts')}: {normal_ai}")
                    if config.image_provider == 'wavespeed':
                        normal_model = config.wavespeed_model_normal if config.wavespeed_model_normal else i18n.t('main_value', value=config.wavespeed_model)
                        print(f"      {i18n.t('wavespeed_model_label')}: {normal_model}")
                    if config.generate_captions:
                        caption_provider_main = getattr(config, 'caption_provider', 'openai')
                        normal_caption = config.caption_provider_normal if config.caption_provider_normal else i18n.t('main_value', value=caption_provider_main)
                        print(f"      {i18n.t('provider_captions')}: {normal_caption}")
    print("\n")
    
    return config

