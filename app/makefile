PYTHON = python
APP = main.py

# Устанавливает зависимости, указанные в pyproject.toml
install:
	poetry install

# Добавляет новый пакет в проект
# Использование: make install-package PACKAGE=<имя_пакета>
install-package:
	poetry add $(PACKAGE)

# Обновляет все зависимости до последних версий
update:
	poetry update

# Запускает основное приложение
run:
	poetry run $(PYTHON) $(APP)

# Очищает файлы .pyc, которые создаются при компиляции Python
clean:
	find . -name "*.pyc" -delete

# Форматирует код по стандарту black
format:
	poetry run black .

# Применяет последние миграции к базе данных
migrate:
	poetry run alembic upgrade head

# Откатывает последнюю миграцию базы данных
downgrade:
	poetry run alembic downgrade -1 

# Создает новую миграцию на основе изменений в моделях
# Использование: make makemigration msg="описание изменений"
makemigration:
	poetry run alembic revision --autogenerate -m "$(msg)"

# Выполняет набор команд для Docker Compose:
# 1. Проставляет текущее состояние миграций.
# 2. Генерирует новую миграцию.
# 3. Применяет миграции.
# 4. Запускает основное приложение.
docker_compose_command:
	cd app && poetry run alembic stamp head && poetry run alembic revision --autogenerate && poetry run alembic upgrade head && poetry run python main.py
