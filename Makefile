.PHONY: install dev test lint docker-up docker-down

install:
	pip install -r requirements.txt
	pip install -e .

dev:
	flask --app dashboards.backend.app run --debug --port 5000

test:
	pytest tests/ -v --tb=short

lint:
	python -m py_compile core/darkwin.py
	python -m py_compile core/config_manager.py
	python -m py_compile core/database.py
	python -m py_compile core/models.py

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

clean:
	rm -rf logs/*.log reports/* __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
