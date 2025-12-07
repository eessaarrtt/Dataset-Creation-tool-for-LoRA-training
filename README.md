# Dataset Creation - LoRA Dataset Creation Tool

**Full-featured Python script for creating image datasets with automatic prompt generation and caption creation for LoRA model training.**

## 📚 Documentation

### Choose your language / Выберите язык:

- 📖 **[Пошаговая инструкция (Step-by-Step Guide)](ИНСТРУКЦИЯ.md)** - Подробное руководство с примерами и советами
- 🇷🇺 **[Русская документация (Russian Documentation)](README_RU.md)** - Полная документация на русском языке
- 🇬🇧 **[English Documentation](README_EN.md)** - Complete documentation in English

---

## ⚠️ Important Notice / Важное уведомление

### Image-to-Video Models / Модели Image-to-Video

⚠️ **In Development / В разработке**: Image-to-Video modules have been added to the script, but full usage scenarios are not yet implemented. These features will be available in future versions. Please do not use Image-to-Video models until the official release.

⚠️ **В разработке**: Модули для генерации видео из изображений добавлены в скрипт, но полные сценарии использования еще не реализованы. Эти функции будут доступны в следующих версиях. Пожалуйста, не используйте Image-to-Video модели до официального релиза.

---

## 📄 License / Лицензия

This project is licensed under **MIT License with Commercial Use Restrictions**. 

**Key points:**
- ✅ Free for personal, educational, and non-commercial use
- ❌ **Commercial use is prohibited** without explicit written permission
- ❌ **Selling, renting, or leasing** this software is not allowed
- 📝 See [LICENSE](LICENSE) file for full terms

**Основные пункты:**
- ✅ Бесплатно для личного, образовательного и некоммерческого использования
- ❌ **Коммерческое использование запрещено** без явного письменного разрешения
- ❌ **Продажа, аренда или лизинг** данного программного обеспечения запрещены
- 📝 См. файл [LICENSE](LICENSE) для полных условий

---

## 📋 System Requirements / Системные требования

### What You Need / Что нужно:

- **Python 3.8+** (3.10+ recommended / рекомендуется 3.10+)
- **pip** (Python package manager / менеджер пакетов Python)
- **Internet connection** (for API requests / для API запросов)
- **API keys** for selected providers (Gemini, OpenAI, Wavespeed)
- **Terminal/Command Line** access (for running the script)

**Операционные системы / Operating Systems:**
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)

**Не требуется / Not Required:**
- ❌ GUI installation (script runs in terminal)
- ❌ Special hardware (works on any computer with Python)
- ❌ Cloud services (all files stored locally)

---

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create config:**
   ```bash
   cp config.example.json config.json
   ```

3. **Add API keys** to `config.json`

4. **Prepare images:**
   - Place at least 2 reference images in `Influencer Reference Images/`
   - Place sample images in `Sample Dataset/`

5. **Run:**
   ```bash
   python main.py
   ```
   
   Or for backward compatibility / Или для обратной совместимости:
   ```bash
   python dataset_creation.py
   ```

---

## 💻 How to Run / Как запустить

### Terminal / Command Line / Терминал

**Windows:**
- Open **Command Prompt** (cmd) or **PowerShell**
- Navigate to project folder: `cd path\to\makenanalog`
- Run: `python main.py`

**macOS / Linux:**
- Open **Terminal**
- Navigate to project folder: `cd /path/to/makenanalog`
- Run: `python main.py` or `python3 main.py`

### IDE (Integrated Development Environment)

You can also run the script from popular IDEs:

- **VS Code**: Open project folder → Right-click `dataset_creation.py` → "Run Python File in Terminal"
- **PyCharm**: Open project → Right-click `dataset_creation.py` → "Run 'dataset_creation'"
- **IDLE** (Python's built-in IDE): File → Open → Select `dataset_creation.py` → Run → Run Module (F5)

### Creating a Shortcut / Создание ярлыка

**Windows** - Create `run.bat`:
```batch
@echo off
cd /d "%~dp0"
python main.py
pause
```

**macOS / Linux** - Create `run.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 main.py
```

Then make it executable: `chmod +x run.sh`

### Double-Click to Run / Запуск двойным кликом

After creating the shortcut files above, you can double-click them to run the script.

---

## ✨ Features

- ✅ Local file storage
- ✅ AI provider selection (Gemini/OpenAI/Grok)
- ✅ Image generation via Wavespeed API
- ✅ Automatic caption generation for LoRA
- ✅ Interactive menu
- ✅ Profile system
- ✅ Multilingual support (Russian/English)
- ✅ Modular architecture for easy maintenance

---

## 📁 Project Structure / Структура проекта

The project is organized in a clean modular structure:

```
makenanalog/
├── src/                    # Main application code / Основной код
│   ├── config.py          # Configuration management
│   ├── file_manager.py    # File system operations
│   ├── prompt_generator.py # AI prompt generation
│   ├── image_generator.py  # Image generation
│   ├── caption_generator.py # Caption generation
│   ├── dataset_creator.py   # Main orchestration
│   ├── interactive_menu.py # Interactive UI
│   └── utils.py           # Utilities
│
├── main.py                 # Entry point / Точка входа
├── dataset_creation.py     # Backward compatibility
├── i18n.py                 # Localization system
└── ...
```

**For detailed structure documentation, see [STRUCTURE.md](STRUCTURE.md)**

**Для подробного описания структуры см. [STRUCTURE.md](STRUCTURE.md)**

---

## 📖 Full Documentation

For detailed instructions, please see:
- 📖 [ИНСТРУКЦИЯ.md](ИНСТРУКЦИЯ.md) - Пошаговая инструкция с примерами (Step-by-step guide with examples)
- 🇷🇺 [README_RU.md](README_RU.md) - Полная документация на русском (Full documentation in Russian)
- 🇬🇧 [README_EN.md](README_EN.md) - Complete documentation in English

---

## 🤝 Contributing

This is a free, open-source project. Contributions are welcome!

Это бесплатный проект с открытым исходным кодом. Вклад приветствуется!

---

## ⚖️ License

See [LICENSE](LICENSE) file for details.

См. файл [LICENSE](LICENSE) для подробностей.
