.PHONY: help install test test-unit test-integration test-coverage clean lint format

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make clean         - Clean up generated files"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code"

install:
	pip install -r requirements.txt
	pip install -r test_requirements.txt
	pip install -e .

test:
	pytest tests/

test-unit:
	pytest tests/ -m unit

test-integration:
	pytest tests/ -m integration

test-coverage:
	pytest tests/ --cov=sellerlegend_api --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".tox" -exec rm -rf {} + 2>/dev/null || true

lint:
	@which flake8 > /dev/null || pip install flake8
	flake8 sellerlegend_api/ tests/

format:
	@which black > /dev/null || pip install black
	black sellerlegend_api/ tests/