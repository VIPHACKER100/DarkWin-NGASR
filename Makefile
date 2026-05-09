# DARKWIN Makefile
# Developed by ARYAN AHIRWAR (VIPHACKER.100)

.PHONY: install dev test lint docker-up docker-down init-db

install:
	pip install -r requirements.txt
	pip install -e .

setup-tools:
	go install github.com/hahwul/dalfox/v2@latest
	go install github.com/lc/gau/v2/cmd/gau@latest
	go install github.com/tomnomnom/qsreplace@latest

dev:
	python core/darkwin.py

test:
	pytest tests/

lint:
	flake8 core/ modules/ pipelines/ ai/

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

init-db:
	python core/migrations/init_db.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf *.egg-info
	rm -f .acknowledged
