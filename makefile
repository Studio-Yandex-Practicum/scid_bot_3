PYTHON = python
APP = app/main.py


install:
	poetry install

install-package:
	poetry add $(PACKAGE)

update:
	poetry update

run:
	poetry run $(PYTHON) $(APP)

clean:
	find . -name "*.pyc" -delete

format:
	poetry run black .

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1 

makemigration:
	alembic revision --autogenerate -m "$(msg)"