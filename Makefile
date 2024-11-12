.PHONY: default lint format

default: format

ifeq ($(OS),Windows_NT)
PYTHON?=py -3.12
else
PYTHON?=python3
endif

lint:
	$(PYTHON) -m black -t py312 --check --diff .

format:
	$(PYTHON) -m black -t py312 . 

.PHONY: test
test:
	$(PYTHON) -m pytest
