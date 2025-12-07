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
10. [Troubleshooting](#troubleshooting)
12. [API Keys](#api-keys)

---

## 📖 Project Description

This project is a Python equivalent of a Make.com workflow for automatically creating image datasets. The script uses AI to generate prompts, creates images through the Wavespeed API, and automatically generates detailed captions for LoRA model training.

### Main Components:

- **Prompt Generation**: Uses Gemini, OpenAI or Grok to analyze reference and sample images
- **Image Generation**: Creates new images through the Wavespeed API
- **Caption Generation**: Automatically creates detailed captions for LoRA training
- **Dataset Packaging**: Creates a zip archive with images and captions

---

## ✨ Features

### Core Functions

- ✅ **Local file storage** (instead of cloud services)
- ✅ **AI provider selection** for prompt generation: **Gemini**, **OpenAI** or **Grok**
- ✅ **Image generation** through **Wavespeed** API
- ✅ **Automatic batch processing** of multiple images
- ✅ **Caption generation** for LoRA training
- ✅ **Interactive menu** with arrow-key navigation and colored output
- ✅ **Profile system** for saving different configurations
- ✅ **Multilingual support** (Russian and English)
- ✅ **Beautiful UI** with colored output and tables

### Supported Models

**AI for Prompts:**
- Gemini 2.5 Flash (fast, free)
- OpenAI GPT-5.1 (only OpenAI model version 5)
- Grok 4.1 Fast Reasoning (from xAI, supports NSFW content)

**Image Generation (Wavespeed):**
- Image-to-Image: `google/nano-banana-pro/edit`, `bytedance/seedream-v4.5/edit`, `bytedance/seedream-v4/edit`
  - Seedream models use `size` parameter (e.g., "1024*1024", "2048*2048", "4096*4096")
  - Nano Banana Pro uses `resolution` parameter (1k, 2k, 4k)
- Image-to-Video: `alibaba/wan-2.5/image-to-video`, `kwaivgi/kling-v2.6-pro/image-to-video`, `kwaivgi/kling-v2.5-turbo-pro/image-to-video` ⚠️ **In Development** - modules are added but usage scenarios are not yet implemented. Will be available in future versions.

**Caption Generation:**
- OpenAI GPT-5.1 (only OpenAI model version 5)
- Grok 4.1 Fast Reasoning (supports NSFW content)

**⚠️ Important about NSFW content:**
- **Only Grok** supports generating prompts and captions for NSFW content
- **Only Seedream v4.5** supports generating images for NSFW content
- **Grok API key is required for NSFW content** (see [API Keys - Grok](#grok) section)
- To work with NSFW content, create an `nsfw/` folder in `Sample Dataset/` and place corresponding images there
- If NSFW content is disabled, files from the `nsfw/` folder will not be processed

---

## 🔧 Requirements

### System Requirements

**Software:**
- **Python 3.8+** (3.10+ recommended)
  - Download from [python.org](https://www.python.org/downloads/)
  - Make sure to check "Add Python to PATH" during installation (Windows)
- **pip** (usually comes with Python)
  - Verify installation: `pip --version`
- **Terminal/Command Line** access
  - Windows: Command Prompt or PowerShell
  - macOS/Linux: Terminal

**Hardware:**
- Any modern computer (no special requirements)
- Internet connection for API requests
- Enough disk space for images and output files

**Accounts & Keys:**
- **API keys** for selected providers:
  - Gemini API key (free, from Google AI Studio)
  - OpenAI API key (paid, from OpenAI Platform)
  - Wavespeed API key (paid, from Wavespeed.ai)
  - **Grok API key (required for NSFW content, from xAI Console)**

**Operating Systems:**
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)

### Python Dependencies

All dependencies are listed in `requirements.txt`:

```bash
# Core dependencies
requests>=2.31.0
urllib3>=2.0.0

# AI providers (choose needed ones)
google-generativeai>=0.3.0  # For Gemini
openai>=1.0.0  # For OpenAI

# Interactive menu
rich>=13.0.0  # For beautiful colored output
inquirer>=3.1.0  # For arrow-key navigation in menu
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

### Step 2: Verify Python Installation

First, make sure Python is installed correctly:

```bash
# Check Python version
python --version
# or
python3 --version

# Check pip installation
pip --version
# or
pip3 --version
```

If Python is not installed:
- **Windows/macOS**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: Use package manager:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3 python3-pip
  
  # Fedora
  sudo dnf install python3 python3-pip
  ```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

### Step 4: Create Configuration

```bash
cp config.example.json config.json
```

### Step 5: Configure config.json

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
  "wavespeed_api_key": "YOUR_WAVESPEED_API_KEY_HERE",
  "grok_api_key": "YOUR_GROK_API_KEY_HERE"
}
```

**Note:** `grok_api_key` is required only if you plan to work with NSFW content.

### Step 6: Prepare Folders

Create necessary folders (or they will be created automatically):

```bash
mkdir -p "Influencer Reference Images"
mkdir -p "Sample Dataset"
mkdir -p "output"
```

---

## 🎯 Quick Start

### Minimal Setup for First Run

1. **Check Python installation:**
   ```bash
   python --version  # Should be 3.8 or higher
   pip --version     # Should show pip version
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create config.json:**
   ```bash
   cp config.example.json config.json
   ```

4. **Add at least one API key** to `config.json`:
   - For Gemini: `gemini_api_key`
   - For OpenAI: `openai_api_key`
   - For Wavespeed: `wavespeed_api_key`
   - **For NSFW content (required):** `grok_api_key`

5. **Prepare images:**
   - Place **at least 2 reference images** in `Influencer Reference Images/`
   - Place **sample images** in `Sample Dataset/`

6. **Run the script:**
   ```bash
   python main.py
   # or
   python3 main.py
   ```
   
   **Note:** For backward compatibility, you can also use `python dataset_creation.py`, but `main.py` is recommended

On first run, an **interactive menu** will appear for selecting all settings!

---

## 📁 Project Structure

The project is organized in a modular structure for better maintainability:

```
makenanalog/
├── src/                          # Main application code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration and profile management
│   ├── file_manager.py          # File system operations
│   ├── prompt_generator.py      # Prompt generation (Gemini/OpenAI/Grok)
│   ├── image_generator.py       # Image generation (Wavespeed)
│   ├── caption_generator.py     # Caption generation for LoRA
│   ├── dataset_creator.py       # Dataset creation orchestration
│   ├── interactive_menu.py     # Interactive menu
│   └── utils.py                 # Utility functions
│
├── main.py                       # Application entry point (recommended)
├── dataset_creation.py          # Backward compatibility file
├── i18n.py                       # Localization system
│
├── config.example.json          # Configuration example
├── config.json                  # Main configuration file
│
├── profiles/                     # Settings profiles
│   └── *.json
│
├── Sample Dataset/               # Sample images
│   ├── normal/                  # Normal content
│   └── nsfw/                    # NSFW content (optional)
│
└── Influencer Reference Images/  # Reference images
```

**Important:**
- Use `main.py` to run the application (recommended)
- `dataset_creation.py` is kept for backward compatibility
- All main modules are in the `src/` folder

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
  "grok_api_key": "your_grok_key",
  "language": "en"
}
```

**Note:** `grok_api_key` is required only if you plan to work with NSFW content.

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
| `grok_api_key` | API key for Grok (required for NSFW content) | - |
| `language` | Interface language (`ru` or `en`) | `ru` |

---

## 💻 How to Run the Script

### Method 1: Terminal / Command Line (Recommended)

**Windows:**
1. Open **Command Prompt** (cmd) or **PowerShell**
   - Press `Win + R`, type `cmd` or `powershell`, press Enter
2. Navigate to project folder:
   ```bash
   cd C:\path\to\makenanalog
   ```
3. Run the script:
   ```bash
   python main.py
   ```

**macOS / Linux:**
1. Open **Terminal**
   - macOS: Press `Cmd + Space`, type "Terminal", press Enter
   - Linux: Press `Ctrl + Alt + T` or find Terminal in applications
2. Navigate to project folder:
   ```bash
   cd /path/to/makenanalog
   ```
3. Run the script:
   ```bash
   python main.py
   # or
   python3 main.py
   ```

### Method 2: IDE (Integrated Development Environment)

You can run the script from popular code editors:

**Visual Studio Code:**
1. Open VS Code
2. File → Open Folder → Select project folder
3. Open `main.py`
4. Right-click → "Run Python File in Terminal"
   - Or press `F5` and select "Python File"

**PyCharm:**
1. Open PyCharm
2. File → Open → Select project folder
3. Right-click `main.py` → "Run 'main'"
   - Or press `Shift + F10`

**IDLE (Python's built-in IDE):**
1. Open IDLE
2. File → Open → Select `main.py`
3. Run → Run Module (or press `F5`)

### Method 3: Create a Shortcut File

**Windows - Create `run.bat`:**
1. Create a new text file named `run.bat` in project folder
2. Add this content:
   ```batch
   @echo off
   cd /d "%~dp0"
   python main.py
   pause
   ```
3. Save and double-click to run

**macOS / Linux - Create `run.sh`:**
1. Create a new file named `run.sh` in project folder
2. Add this content:
   ```bash
   #!/bin/bash
   cd "$(dirname "$0")"
   python3 main.py
   ```
3. Make it executable:
   ```bash
   chmod +x run.sh
   ```
4. Double-click or run: `./run.sh`

### Method 4: Jupyter Notebook (Advanced)

If you want to run parts of the script interactively:
1. Install Jupyter: `pip install jupyter`
2. Create a notebook: `jupyter notebook`
3. Import and use functions from modules in the `src/` folder

---

## 💻 Usage

### Interactive Mode (Recommended)

```bash
python main.py
```

**Note:** For backward compatibility, you can also use `python dataset_creation.py`, but `main.py` is recommended

An interactive menu will appear with:
- **Arrow-key navigation** (if `inquirer` is installed)
- **Colored output** with tables and panels (if `rich` is installed)
- **Fallback mode** with simple text input if libraries are not installed

Example:
```
╔════════════════════════════════════════════════════════╗
║        🎨 Dataset Creation - Interactive Setup         ║
╚════════════════════════════════════════════════════════╝

1️⃣  AI provider for prompt generation:
   Current value: gemini
   
   [1] Gemini
   [2] OpenAI
   
   Your choice: [Use arrow keys to navigate]
```

### 📊 Interactive Menu Flow Diagrams

#### Main Menu Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Profile Selection                                     │
│    ├─ [1-N] Select existing profile                     │
│    ├─ [0] Create new profile                            │
│    └─ [Enter] Skip (temporary settings)                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. NSFW Content Question                                │
│    ├─ [1] Yes → Auto-configured:                        │
│    │      • Grok for NSFW prompts                       │
│    │      • Seedream v4.5 for NSFW generation           │
│    │      • Grok for NSFW captions                       │
│    │      → Proceed to normal content setup             │
│    │                                                    │
│    ├─ [2] No → Main settings apply to all content       │
│    │                                                    │
│    └─ [Enter] Skip → = "No"                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. AI Provider for Prompts                              │
│    (If NSFW=Yes: for normal content)                    │
│    (If NSFW=No: for all content)                       │
│    ├─ [1] Gemini                                        │
│    ├─ [2] OpenAI (GPT-5.1)                              │
│    ├─ [3] Grok                                          │
│    └─ [Enter] Use from config/profile                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Processing Mode                                      │
│    ├─ [1] bulk - Batch processing                      │
│    ├─ [2] detailed - Single image                      │
│    └─ [Enter] Use from config/profile                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Image Generation Provider                            │
│    (If NSFW=Yes: for normal content)                    │
│    ├─ [1] Wavespeed                                     │
│    └─ [Enter] Use from config/profile                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Wavespeed Model                                      │
│    (If NSFW=Yes: for normal content)                    │
│    ├─ [1] nano-banana-pro/edit                          │
│    ├─ [2] seedream-v4.5/edit                            │
│    ├─ [3] seedream-v4/edit                              │
│    ├─ [4-6] Video models (⚠️ In development)            │
│    └─ [Enter] Use from config/profile                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 7. Resolution                                           │
│    ├─ [1] 1k (1920×1920)                                │
│    ├─ [2] 2k (2048×2048)                                │
│    ├─ [3] 4k (4096×4096)                                │
│    └─ [Enter] Use from config/profile                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 8. Caption Generation                                   │
│    (If NSFW=Yes: for normal content)                    │
│    ├─ [1] Yes → Proceed to step 9                      │
│    ├─ [2] No → Skip captions                            │
│    └─ [Enter] Use from config/profile                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 9. Trigger Name (only if captions=Yes)                  │
│    └─ Enter character name (one word)                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 10. Caption Provider (only if captions=Yes)             │
│     ├─ [1] OpenAI → Auto GPT-5.1                        │
│     ├─ [2] Grok → Auto grok-4-1-fast-reasoning          │
│     └─ [Enter] Use from config/profile                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 11. Final Summary                                       │
│     └─ Shows all selected settings                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 12. Save Profile                                        │
│     ├─ [1] Yes → Enter profile name → Save              │
│     └─ [2] No → Skip                                    │
└─────────────────────────────────────────────────────────┘
```

#### Scenario 1: NSFW Content Enabled

```
NSFW = Yes
  │
  ├─ Auto-configured for NSFW:
  │   • AI Provider: Grok
  │   • Prompt Model: grok-4-1-fast-reasoning
  │   • Wavespeed Model: seedream-v4.5/edit
  │   • Caption Provider: Grok
  │   • Caption Model: grok-4-1-fast-reasoning
  │
  └─ Settings for Normal Content:
      ├─ AI Provider: [Choice: Gemini/OpenAI/Grok]
      ├─ Mode: [Choice: bulk/detailed]
      ├─ Wavespeed Model: [Choice: nano-banana/seedream-v4/seedream-v4.5]
      ├─ Resolution: [Choice: 1k/2k/4k]
      ├─ Captions: [Choice: Yes/No]
      │   └─ If Yes:
      │       ├─ Trigger Name: [Input]
      │       └─ Caption Provider: [Choice: OpenAI/Grok]
      │           ├─ OpenAI → GPT-5.1
      │           └─ Grok → grok-4-1-fast-reasoning
      └─ Result: Different settings for NSFW and normal
```

#### Scenario 2: NSFW Content Disabled

```
NSFW = No (or Enter)
  │
  └─ Main Settings (apply to all content):
      ├─ AI Provider: [Choice: Gemini/OpenAI/Grok]
      ├─ Mode: [Choice: bulk/detailed]
      ├─ Wavespeed Model: [Choice: nano-banana/seedream-v4/seedream-v4.5]
      ├─ Resolution: [Choice: 1k/2k/4k]
      ├─ Captions: [Choice: Yes/No]
      │   └─ If Yes:
      │       ├─ Trigger Name: [Input]
      │       └─ Caption Provider: [Choice: OpenAI/Grok]
      │           ├─ OpenAI → GPT-5.1
      │           └─ Grok → grok-4-1-fast-reasoning
      └─ Result: Same settings for all content
```

#### Possible Combinations Matrix

| NSFW | AI Provider | Wavespeed Model | Captions | Caption Provider | Result |
|------|-------------|-----------------|----------|------------------|--------|
| Yes  | Gemini      | nano-banana     | Yes      | OpenAI           | NSFW: Grok+Seedream v4.5, Normal: Gemini+nano-banana+OpenAI |
| Yes  | OpenAI      | seedream-v4     | Yes      | Grok             | NSFW: Grok+Seedream v4.5, Normal: OpenAI+seedream-v4+Grok |
| Yes  | Grok        | seedream-v4.5   | No       | -                | NSFW: Grok+Seedream v4.5, Normal: Grok+seedream-v4.5 |
| No   | Gemini      | nano-banana     | Yes      | OpenAI           | All: Gemini+nano-banana+OpenAI |
| No   | OpenAI      | seedream-v4     | Yes      | Grok             | All: OpenAI+seedream-v4+Grok |
| No   | Grok        | seedream-v4.5   | No       | -                | All: Grok+seedream-v4.5 |

#### Important Notes

1. **Auto NSFW Settings** (if NSFW=Yes):
   - Cannot be changed through menu
   - Always: Grok + Seedream v4.5 + Grok for captions

2. **Skipping Steps** (Enter):
   - Uses values from config.json or profile
   - If no value → uses default

3. **Required Steps**:
   - Image generation provider (Wavespeed) - must be selected
   - Trigger name - required if captions=Yes

4. **File Processing**:
   - If NSFW=Yes: files from `nsfw/` processed with NSFW settings
   - If NSFW=No: files from `nsfw/` **are NOT processed**
   - Files from `normal/` always processed with normal content settings

---

### Non-Interactive Mode

```bash
python main.py --no-interactive
```

Uses only settings from `config.json` and command-line arguments.

### With Command-Line Arguments

```bash
# Use OpenAI instead of Gemini
python main.py --ai-provider openai --no-interactive

# Use specific profile
python main.py --profile my_profile --no-interactive

# Specify different config file
python main.py --config my_config.json
```

### Full List of Arguments

```bash
python main.py --help
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
python main.py --profile production

# Show list of all profiles
python main.py --list-profiles
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

## 🔄 Updating the Script

The script supports automatic updates via git. If you installed the script using `git clone`, you can receive updates "over-the-air" without re-downloading.

### Checking for Updates

```bash
# Check for available updates
python main.py --check-updates
```

This command will show:
- Current version (commit and branch)
- Number of available updates
- List of recent changes

### Updating the Script

```bash
# Update script to latest version
python main.py --update
```

**What happens during update:**
1. Script checks for uncommitted changes
2. If changes exist, offers to save them to temporary storage (stash)
3. Executes `git pull` to fetch updates
4. Shows update result

### Force Update

If you need to force update the script (reset local changes):

```bash
# Force update (reset local changes)
python main.py --force-update
```

⚠️ **Warning:** This command will delete all uncommitted changes!

### Automatic Update Check on Startup

To automatically check for updates on every startup:

```bash
# Run with automatic update check
python main.py --auto-update-check
```

If updates are found, the script will offer to update.

### Requirements for Updates

- Script must be installed via `git clone` (not just downloaded as zip)
- Git must be installed on your computer
- Repository must be connected to remote repository (origin)

### If Updates Don't Work

1. **Check if it's a git repository:**
   ```bash
   ls -la .git  # .git folder should exist
   ```

2. **Check connection to remote repository:**
   ```bash
   git remote -v  # Should show origin
   ```

3. **Install git:**
   - Windows: [git-scm.com](https://git-scm.com/download/win)
   - macOS: `brew install git` or install Xcode Command Line Tools
   - Linux: `sudo apt-get install git` (Ubuntu/Debian)

### First Installation via Git

If you haven't installed the script via git yet:

```bash
# Clone the repository
git clone https://github.com/your-username/makenanalog.git
cd makenanalog

# Install dependencies
pip install -r requirements.txt
```

After this, you can use update commands.

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
- Seedream v4.5: $0.04 per image (any resolution)
- Seedream v4: $0.027 per image (any resolution)
- Video models: depends on duration

#### Grok

**⚠️ Required for NSFW content!**

1. Go to [xAI Console](https://console.x.ai/)
2. Register or sign in
3. Navigate to "API Keys" or "Settings" section
4. Create a new API key
5. Copy the key and add to `config.json`:
   ```json
   "grok_api_key": "your_key_here"
   ```

**Features:**
- Paid service (from xAI, Elon Musk's company)
- NSFW content support for prompts and captions
- Uses OpenAI-compatible API
- Model: `grok-4-1-fast-reasoning` (recommended)

**Pricing:**
- Depends on model and usage
- Check current prices at [xAI Console](https://console.x.ai/)

**⚠️ Important:**
- Grok API key is **required** for working with NSFW content
- Without Grok API key, you cannot generate prompts and captions for NSFW images
- Grok is the only provider that supports NSFW content

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

