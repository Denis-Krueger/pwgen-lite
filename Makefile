PYTHON ?= python3
VENV_DIR := .venv
VENV_PY := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

.PHONY: help venv install test run lint clean

help:
	@echo "Targets:"
	@echo "  make venv      - create virtual environment in .venv"
	@echo "  make install   - install dev dependencies (pytest)"
	@echo "  make test      - run pytest"
	@echo "  make run ARGS=\"16 --symbols\" - run pwgen with ARGS"
	@echo "  make clean     - remove .venv and caches"

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_PIP) install -U pip
	$(VENV_PIP) install pytest

test: install
	$(VENV_PY) -m pytest

run: install
	$(VENV_PY) pwgen.py $(ARGS)

clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__ .pytest_cache
	rm -rf tests/__pycache__