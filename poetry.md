# 📦 Poetry + Dev Workflow Setup (macOS)

> Полная инструкция для настройки Python-проекта с Poetry, Pre-commit и Makefile.

---

## ✅ Установка Poetry (macOS)

1. Установи Poetry:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
2. Добавь Poetry в PATH
   ```bash
   nano ~/.zshrc
    ```
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

   Сохрани: Ctrl + O → Enter, затем Ctrl + X

3. Примени изменения:
   ```bash
   source ~/.zshrc
   ```

4. Проверь установку:
   ```bash
   poetry --version
   ```

## 📁 Инициализация проекта

В корне проекта:
```bash
poetry init
```
📦 Установка зависимостей

Установи все зависимости, включая dev-зависимости:
```bash
poetry install --with dev # или make install
```
🔍 Проверка окружения
```bash
poetry env info
poetry env list
```

