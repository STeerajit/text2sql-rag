# Text2SQL RAG System Makefile

.PHONY: help install test clean dev-install run eval format lint docs

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install the package"
	@echo "  make dev-install  - Install in development mode"
	@echo "  make test         - Run tests"
	@echo "  make eval         - Run evaluation"
	@echo "  make run          - Run interactive mode"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Run linting"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make docs         - Generate documentation"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pip install -r requirements.txt

# Running
run:
	python main.py -i

# Testing and Evaluation
test:
	python -m pytest tests/ -v

test-unit:
	python tests/unit/simple_comprehensive_test.py

test-integration:
	python tests/integration/comprehensive_evaluation.py

test-benchmarks:
	python tests/benchmarks/performance_test.py

eval:
	python tests/integration/comprehensive_evaluation.py

eval-simple:
	python tests/unit/simple_comprehensive_test.py

# Code Quality
format:
	black src/ tests/ *.py

beautify:
	python scripts/beautify_code.py
	python scripts/clean_emojis.py
	python scripts/clean_readme.py

lint:
	flake8 src/ tests/ *.py
	mypy src/

clean-code: beautify format lint

# Cleaning
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "README.md contains all documentation"

# Quick commands
question:
	python main.py -q "$(QUESTION)"

batch:
	python main.py -f configs/sample_questions.json

# Example usage:
# make question QUESTION="แสดงจำนวนผู้ป่วยแต่ละโรงพยาบาล"
