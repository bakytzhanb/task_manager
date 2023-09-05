all: build up build_db test pre-commit clear

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

build_db:
	docker-compose run --rm --no-deps task_manager python manage.py migrate

test:
	docker-compose run task_manager pytest

pre-commit:
	pre-commit run --all-files

requirements:
	pip install --upgrade pip && pip install -r requirements.txt

clear:
	find . -name \*.pyc -delete
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
