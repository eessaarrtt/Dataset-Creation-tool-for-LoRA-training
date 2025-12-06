# Dataset Creation - LoRA Dataset Creation Tool

**Full-featured Python script for creating image datasets with automatic prompt generation and caption creation for LoRA model training.**

## 📚 Documentation

### Choose your language / Выберите язык:

- 🇷🇺 **[Русская инструкция (Russian Guide)](README_RU.md)** - Полная пошаговая инструкция на русском языке
- 🇬🇧 **[English Guide](README_EN.md)** - Complete step-by-step guide in English

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
   python dataset_creation.py
   ```

---

## ✨ Features

- ✅ Local file storage
- ✅ AI provider selection (Gemini/OpenAI)
- ✅ Image generation via Wavespeed API
- ✅ Automatic caption generation for LoRA
- ✅ Interactive menu
- ✅ Profile system
- ✅ Multilingual support (Russian/English)

---

## 📖 Full Documentation

For detailed instructions, please see:
- 🇷🇺 [README_RU.md](README_RU.md) - Полная инструкция на русском
- 🇬🇧 [README_EN.md](README_EN.md) - Complete guide in English

---

## 🤝 Contributing

This is a free, open-source project. Contributions are welcome!

Это бесплатный проект с открытым исходным кодом. Вклад приветствуется!

---

## ⚖️ License

See [LICENSE](LICENSE) file for details.

См. файл [LICENSE](LICENSE) для подробностей.
