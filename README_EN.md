# Dataset Creation - LoRA Dataset Creation Tool

A full-featured Python script for creating image datasets with automatic prompt generation and caption creation for LoRA model training.

## 📋 Table of Contents

1. [Project Description](#project-description)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Detailed Configuration](#detailed-configuration)
7. [Usage](#usage)
8. [Caption Generation for LoRA](#caption-generation-for-lora)
9. [Profile System](#profile-system)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)
12. [API Keys](#api-keys)

---

## 📖 Project Description

This project is a Python equivalent of a Make.com workflow for automatically creating image datasets. The script uses AI to generate prompts, creates images through the Wavespeed API, and automatically generates detailed captions for LoRA model training.

### Main Components:

- **Prompt Generation**: Uses Gemini or OpenAI to analyze reference and sample images
- **Image Generation**: Creates new images through the Wavespeed API
- **Caption Generation**: Automatically creates detailed captions for LoRA training
- **Dataset Packaging**: Creates a zip archive with images and captions

---

## ✨ Features

### Core Functions

- ✅ **Local file storage** (instead of cloud services)
- ✅ **AI provider selection** for prompt generation: **Gemini** or **OpenAI**
- ✅ **Image generation** through **Wavespeed** API
- ✅ **Automatic batch processing** of multiple images
- ✅ **Caption generation** for LoRA training
- ✅ **Interactive menu** for configuring all parameters
- ✅ **Profile system** for saving different configurations
- ✅ **Multilingual support** (Russian and English)

### Supported Models

**AI for Prompts:**
- Gemini 2.5 Flash (fast, free)
- OpenAI GPT-5.1, GPT-4o (only models with vision support)

**Image Generation (Wavespeed):**
- Image-to-Image: `google/nano-banana-pro/edit`, `bytedance/seedream-v4.5`, `bytedance/seedream-v4`
- Image-to-Video: `alibaba/wan-2.5/image-to-video`, `kwaivgi/kling-v2.6-pro/image-to-video`, `kwaivgi/kling-v2.5-turbo-pro/image-to-video` ⚠️ **In Development** - modules are added but usage scenarios are not yet implemented. Will be available in future versions.

**Caption Generation:**
- OpenAI GPT-5.1, GPT-4o (only models with vision support)

---

## 🔧 Requirements

### System Requirements

- **Python 3.8+** (3.10+ recommended)
- **Internet connection** for API requests
- **API keys** for selected providers

### Python Dependencies

All dependencies are listed in `requirements.txt`:

```bash
# Core dependencies
requests>=2.31.0
urllib3>=2.0.0

# AI providers (choose needed ones)
google-generativeai>=0.3.0  # For Gemini
openai>=1.0.0  # For OpenAI
```

---

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd makenanalog

# Or simply download and extract the archive
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Create Configuration

```bash
cp config.example.json config.json
```

### Step 4: Configure config.json

Open `config.json` and specify:

1. **Folder paths** (can be left as default)
2. **API keys** for selected providers

```json
{
  "influencer_ref_folder": "./Influencer Reference Images",
  "sample_dataset_folder": "./Sample Dataset",
  "output_folder": "./output",
  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
  "openai_api_key": "YOUR_OPENAI_API_KEY_HERE",
  "wavespeed_api_key": "YOUR_WAVESPEED_API_KEY_HERE"
}
```

### Step 5: Prepare Folders

Create necessary folders (or they will be created automatically):

```bash
mkdir -p "Influencer Reference Images"
mkdir -p "Sample Dataset"
mkdir -p "output"
```

---

## 🎯 Quick Start

### Minimal Setup for First Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create config.json:**
   ```bash
   cp config.example.json config.json
   ```

3. **Add at least one API key** to `config.json`:
   - For Gemini: `gemini_api_key`
   - For OpenAI: `openai_api_key`
   - For Wavespeed: `wavespeed_api_key`

4. **Prepare images:**
   - Place **at least 2 reference images** in `Influencer Reference Images/`
   - Place **sample images** in `Sample Dataset/`

5. **Run the script:**
   ```bash
   python dataset_creation.py
   ```

On first run, an **interactive menu** will appear for selecting all settings!

---

## ⚙️ Detailed Configuration

### config.json Structure

```json
{
  "influencer_ref_folder": "./Influencer Reference Images",
  "sample_dataset_folder": "./Sample Dataset",
  "output_folder": "./output",
  "limit_ref_images": 10,
  "limit_sample_images": 10,
  "gemini_api_key": "your_gemini_key",
  "openai_api_key": "your_openai_key",
  "wavespeed_api_key": "your_wavespeed_key",
  "language": "en"
}
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `influencer_ref_folder` | Path to reference images folder | `./Influencer Reference Images` |
| `sample_dataset_folder` | Path to sample images folder | `./Sample Dataset` |
| `output_folder` | Folder for saving results | `./output` |
| `limit_ref_images` | Maximum number of reference images | `10` |
| `limit_sample_images` | Maximum number of sample images | `10` |
| `gemini_api_key` | API key for Gemini | - |
| `openai_api_key` | API key for OpenAI | - |
| `wavespeed_api_key` | API key for Wavespeed | - |
| `language` | Interface language (`ru` or `en`) | `ru` |

---

## 💻 Usage

### Interactive Mode (Recommended)

```bash
python dataset_creation.py
```

An interactive menu will appear:

```
============================================================
  🎨 Dataset Creation - Interactive Setup
============================================================

Select settings (Enter to use values from config.json):

1️⃣  AI provider for prompt generation:
   Current value: gemini
   [1] Gemini (fast, free with limits)
   [2] OpenAI (accurate, paid)
   Your choice (1/2 or Enter to skip): 
```

### Non-Interactive Mode

```bash
python dataset_creation.py --no-interactive
```

Uses only settings from `config.json` and command-line arguments.

### With Command-Line Arguments

```bash
# Use OpenAI instead of Gemini
python dataset_creation.py --ai-provider openai --no-interactive

# Use specific profile
python dataset_creation.py --profile my_profile --no-interactive

# Specify different config file
python dataset_creation.py --config my_config.json
```

### Full List of Arguments

```bash
python dataset_creation.py --help
```

---

## 📝 Caption Generation for LoRA

### What are LoRA Captions?

Captions are text descriptions of images used for LoRA model training. The more detailed the description, the better the model will "remember" character traits.

### How Caption Generation Works

1. **After image generation**, the script offers to create captions
2. **Specify trigger name** - a keyword that will be used in every caption
3. **OpenAI analyzes the image** and creates a detailed description
4. **Files are created:**
   - `trigger_name_0001.txt` - caption for the first image
   - `trigger_name_0002.txt` - caption for the second image
   - etc.
5. **Images are renamed:**
   - `trigger_name_0001.png`
   - `trigger_name_0002.png`
   - etc.
6. **Zip archive is created** `trigger_name_lora_dataset.zip` with all files

### Caption Example

**Bad:**
```
Elara
```

**Good:**
```
Elara with blonde hair, wearing a blue dress, standing in a garden, sunny day, detailed face, full body portrait
```

### Configuring Caption Generation

In the interactive menu, you can select:

1. **Whether to generate captions** (Yes/No)
2. **Trigger name**
3. **OpenAI model** for caption generation:
   - GPT-5.1 (recommended, best quality, supports vision)
   - GPT-4o (proven model, supports vision)
   
   **⚠️ Note:** GPT-5 Nano and GPT-5 Mini do not support image analysis and cannot be used for captions.

### lora_dataset Folder Structure

```
output/
└── lora_dataset/
    ├── trigger_name_0001.png
    ├── trigger_name_0001.txt
    ├── trigger_name_0002.png
    ├── trigger_name_0002.txt
    └── ...
```

And zip archive:
```
output/
└── trigger_name_lora_dataset.zip
```

---

## 👤 Profile System

Profiles allow saving different configurations for different tasks.

### Creating a Profile

1. Run the script in interactive mode
2. Select all needed settings
3. At the end, the script will offer to save settings as a profile
4. Enter profile name (e.g., `production`, `testing`, `character1`)

### Using a Profile

```bash
# Use specific profile
python dataset_creation.py --profile production

# Show list of all profiles
python dataset_creation.py --list-profiles
```

### Where Profiles are Stored

Profiles are saved in the `profiles/` folder:

```
profiles/
├── production.json
├── testing.json
└── character1.json
```

### What's Saved in a Profile

- AI provider and model
- Image generation provider and model
- Prompt template (bulk/detailed)
- Resolution and output format
- Caption generation settings
- Trigger name

**Not saved in profile:**
- API keys (stored in `config.json`)
- Folder paths (stored in `config.json`)

---

## 🧪 Testing

### Test Prompt Generation (Without Image Costs)

```bash
python test_prompt_only.py
```

This script checks the AI provider without generating images.

### Test OpenAI Models

```bash
# Test all models
python test_openai_models.py

# Test one model
python test_openai_models.py --model gpt-5.1

# Test caption generation and file creation
python test_openai_models.py --test-captions

# Test with custom trigger name
python test_openai_models.py --test-captions --trigger-name "my_character"
```

### Test with One Image

1. Set in `config.json`: `"limit_sample_images": 1`
2. Run the script:
   ```bash
   python dataset_creation.py --no-interactive
   ```

### Check Results

After testing, check:

1. **output/** folder - prompts and images should be created
2. **output/lora_dataset/** folder - if caption generation is enabled
3. **Zip archive** - if caption generation is enabled

---

## 🔍 Troubleshooting

### Error "API key not set"

**Problem:** Script cannot find API key for selected provider.

**Solution:**
1. Check that you filled in the corresponding key in `config.json`
2. Make sure `config.json` file exists
3. Check key correctness (no extra spaces, quotes)

### Error "Folder not found"

**Problem:** Script cannot find image folder.

**Solution:**
1. Create folders `Influencer Reference Images` and `Sample Dataset`
2. Check paths in `config.json`
3. Make sure folders contain images (at least 2 in reference folder)

### Error importing libraries

**Problem:** Python cannot find required libraries.

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific libraries
pip install google-generativeai  # For Gemini
pip install openai  # For OpenAI
pip install requests  # For HTTP requests
```

### Error generating image

**Problem:** Wavespeed API returned an error.

**Solution:**
1. Check Wavespeed API key balance
2. Make sure model is specified correctly
3. Check internet connection
4. Look at `*_response.json` files in output folder for error details

### Error "Model not supported"

**Problem:** Selected model doesn't support needed function.

**Solution:**
- For image-to-image use: `google/nano-banana-pro/edit`, `bytedance/seedream-v4.5`, `bytedance/seedream-v4`
- ⚠️ **Image-to-Video Models**: Modules for generating videos from images have been added to the script, but full usage scenarios are not yet implemented. These features will be available in future versions of the project. Please do not use Image-to-Video models until the official release of this functionality.

### Files are overwritten

**Problem:** On rerun, files with same names are overwritten.

**Solution:** Script automatically adds timestamps to filenames to avoid overwriting. If you see overwriting, check logs.

---

## 🔑 API Keys

### Getting API Keys

#### Gemini

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key and add to `config.json`:
   ```json
   "gemini_api_key": "your_key_here"
   ```

**Features:**
- Free with limits (60 requests/min)
- Fast response
- Good prompt quality

#### OpenAI

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in
3. Click "Create new secret key"
4. Copy key and add to `config.json`:
   ```json
   "openai_api_key": "your_key_here"
   ```

**Features:**
- Paid (but has free credit for new users)
- High quality
- GPT-5 model support

**Available models for captions (with vision support):**
- GPT-5.1: $1.250 / 1M input, $10.000 / 1M output (recommended for captions)
- GPT-4o: $2.50 / 1M input, $10.00 / 1M output (proven model)

**⚠️ Important:** GPT-5 Nano and GPT-5 Mini do not support image analysis (vision API) and cannot be used for caption generation.

#### Wavespeed

1. Go to [Wavespeed](https://wavespeed.ai)
2. Register or sign in
3. Go to API Keys section
4. Create new key
5. Add to `config.json`:
   ```json
   "wavespeed_api_key": "your_key_here"
   ```

**Features:**
- Paid service
- Multiple models for different tasks
- High quality generation

**Model Prices:**
- Nano Banana Pro Edit: $0.14 (1k/2k), $0.24 (4k)
- Seedream v4.5: $0.04 per image
- Seedream v4: $0.04 per image
- Video models: depends on duration

### API Key Security

⚠️ **Important:**
- Never publish `config.json` with real keys
- Add `config.json` to `.gitignore`
- Use `config.example.json` for template
- Regularly check key usage
- If key is leaked - immediately revoke it and create new one

---

---

## 📄 License

Use freely for your projects.

---

## 🤝 Support

If you encounter problems or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Study additional documentation
3. Check console logs
4. Check `*_response.json` files in output folder

---

**Good luck creating datasets! 🚀**

