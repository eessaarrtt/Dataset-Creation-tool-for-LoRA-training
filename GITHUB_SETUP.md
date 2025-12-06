# Инструкция по загрузке проекта на GitHub

## Шаг 1: Создание репозитория на GitHub

1. Войдите в свой аккаунт GitHub
2. Нажмите кнопку **"New"** или **"+"** → **"New repository"**
3. Заполните форму:
   - **Repository name**: `makenanalog` (или другое имя)
   - **Description**: "Dataset Creation - LoRA Dataset Creation Tool"
   - **Visibility**: Public или Private (на ваше усмотрение)
   - **НЕ** добавляйте README, .gitignore или LICENSE (мы уже создали их)
4. Нажмите **"Create repository"**

## Шаг 2: Инициализация Git в проекте

Откройте терминал в папке проекта и выполните:

```bash
# Инициализация git репозитория
git init

# Добавление всех файлов (кроме тех, что в .gitignore)
git add .

# Первый коммит
git commit -m "Initial commit: Dataset Creation tool for LoRA training"

# Добавление удаленного репозитория (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/makenanalog.git

# Переименование основной ветки в main (если нужно)
git branch -M main

# Отправка на GitHub
git push -u origin main
```

## Шаг 3: Проверка

После успешной загрузки:
1. Откройте ваш репозиторий на GitHub
2. Убедитесь, что все файлы загружены
3. Проверьте, что README.md отображается корректно
4. Проверьте, что LICENSE файл виден

## Важные файлы, которые должны быть в репозитории:

✅ `dataset_creation.py` - основной скрипт
✅ `i18n.py` - модуль локализации
✅ `config.example.json` - пример конфигурации
✅ `requirements.txt` - зависимости
✅ `README.md` - главный README
✅ `README_RU.md` - русская инструкция
✅ `README_EN.md` - английская инструкция
✅ `LICENSE` - лицензия
✅ `.gitignore` - игнорируемые файлы

## Файлы, которые НЕ должны быть в репозитории (уже в .gitignore):

❌ `config.json` - содержит API ключи
❌ `profiles/` - содержит пользовательские профили
❌ `output/` - выходные файлы
❌ `*.log` - логи
❌ `__pycache__/` - кэш Python

## Дополнительные настройки (опционально)

### Добавление описания репозитория

На странице репозитория нажмите ⚙️ (Settings) → в разделе "About" добавьте:
- **Description**: "Dataset Creation - LoRA Dataset Creation Tool"
- **Topics**: `python`, `lora`, `ai`, `image-generation`, `dataset-creation`

### Добавление badges (опционально)

Можно добавить в README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT%20with%20restrictions-red.svg)
```

---

## Обновление проекта

После внесения изменений:

```bash
# Проверка изменений
git status

# Добавление изменений
git add .

# Коммит с описанием
git commit -m "Описание изменений"

# Отправка на GitHub
git push
```

---

## Troubleshooting

### Ошибка: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/makenanalog.git
```

### Ошибка: "Permission denied"
- Проверьте правильность URL репозитория
- Убедитесь, что у вас есть права на запись в репозиторий
- Возможно, нужно использовать SSH вместо HTTPS

### Если забыли добавить .gitignore
```bash
# Удалить уже добавленные файлы из индекса
git rm -r --cached config.json profiles/ output/

# Добавить изменения
git add .gitignore

# Коммит
git commit -m "Add .gitignore and remove sensitive files"
```

