.PHONY: default lint format

default: format

ifeq ($(OS),Windows_NT)
PYTHON?=py -3.8
else
PYTHON?=python3
endif

lint:
	$(PYTHON) -m black -t py38 --check --diff .

format:
	$(PYTHON) -m black -t py38 . 
