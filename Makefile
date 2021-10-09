.PHONY: default lint format

default: format

lint:
	py -3.8 -m black -t py38 --check --diff .

format:
	py -3.8 -m black -t py38 . 
