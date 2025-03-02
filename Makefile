.PHONY: up down clean mage setup test lint

# Project configuration
PROJECT_NAME ?= mage_gcp_covid
PYTHON_VERSION ?= 3.9

# Mage AI specific settings
MAGE_PORT = 6789
MAGE_IMAGE = mageai/mageai

# Docker volumes for persistence
MAGE_VOLUME = $(PROJECT_NAME)_mage_data

# Development environment
setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

# Linting and code quality
lint:
	. venv/bin/activate && \
	flake8 . && \
	black . --check && \
	isort . --check-only

# Testing
test:
	. venv/bin/activate && pytest tests/

# Start Mage AI with project persistence
mage:
	docker run -it \
		-p $(MAGE_PORT):$(MAGE_PORT) \
		-v $(PWD):/home/src \
		-v $(MAGE_VOLUME):/root/.mage \
		-e GOOGLE_APPLICATION_CREDENTIALS=/home/src/credentials/gcp-credentials.json \
		$(MAGE_IMAGE) \
		/app/run_app.sh mage start $(PROJECT_NAME)

# Quick start with different project name
# Usage: make start-mage PROJECT_NAME=your_project_name
start-mage: mage

# Stop any running Mage containers
mage-stop:
	docker ps -q --filter ancestor=$(MAGE_IMAGE) | xargs -r docker stop

# Remove Mage containers and volume
mage-clean:
	docker ps -aq --filter ancestor=$(MAGE_IMAGE) | xargs -r docker rm
	docker volume rm -f $(MAGE_VOLUME)

# Full restart of Mage
mage-restart: mage-stop mage-clean mage

# Clean Python artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .tox/

# Full environment setup
init: setup lint test

# Help target
help:
	@echo "Available targets:"
	@echo "  setup        : Set up Python virtual environment and install dependencies"
	@echo "  mage         : Start Mage AI container"
	@echo "  start-mage   : Start Mage AI with custom project name"
	@echo "  mage-stop    : Stop Mage AI container"
	@echo "  mage-clean   : Remove Mage AI container and volume"
	@echo "  mage-restart : Restart Mage AI container"
	@echo "  lint         : Run code quality checks"
	@echo "  test         : Run tests"
	@echo "  clean        : Clean Python artifacts"
	@echo "  init         : Full environment setup"
MAGE_PORT = 6789
MAGE_IMAGE = mageai/mageai

# Start Mage AI
mage:
	docker run -it \
		-p $(MAGE_PORT):$(MAGE_PORT) \
		-v $(PWD):/home/src \
		$(MAGE_IMAGE) \
		/app/run_app.sh mage start $(PROJECT_NAME)

# Quick start with different project name
# Usage: make start-mage PROJECT_NAME=your_project_name
start-mage: mage

# Stop any running Mage containers
mage-stop:
	docker ps -q --filter ancestor=$(MAGE_IMAGE) | xargs -r docker stop

# Remove Mage containers
mage-clean:
	docker ps -aq --filter ancestor=$(MAGE_IMAGE) | xargs -r docker rm

# Full restart
mage-restart: mage-stop mage-clean mage