FROM python:3.12.0
WORKDIR /app

# Установка необходимых системных зависимостей (если нужно)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Установка пути для Poetry
ENV PATH="/root/.local/bin:$PATH"

# Копирование только pyproject.toml
COPY pyproject.toml ./

# указываем poetry использовать venv проекта
RUN  poetry config virtualenvs.in-project true

# Установка зависимостей
RUN poetry install --no-root

# Копирование остальных файлов, включая alembic
COPY . .

# Команда для запуска приложения
CMD ["poetry", "run", "python", "app/main.py"]
