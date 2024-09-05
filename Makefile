PROJECT_HOME := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

SHELL = /bin/bash

-include .env

.PHONY: env
env:
	pyenv install -s 3.10.6
	pyenv local 3.10.6
	pyenv exec python -m venv venv
	source venv/bin/activate && \
	pip install --upgrade pip && \
	pip install --upgrade certifi && \
	pip install poetry && \
	poetry self update && \
	poetry install

.PHONY: clean
clean:
	cd $(PROJECT_HOME) && \
	find repenseai/ -name __pycache__ -exec rm -r {} + && \
	find tests/ -name __pycache__ -exec rm -r {} + && \
	rm -rf dist/ *.egg-info/ __pycache__/ .pytest_cache/ .mypy_cache/


.PHONY: package
package:
	cd $(PROJECT_HOME) && \
	rm -rf dist/ && \
	poetry build


.PHONY: publish
publish: package
	cd $(PROJECT_HOME) && \
	poetry publish -r ifood-data-prd-pypi


.PHONY: lint
lint:
	black repenseai/ tests/
	flake8 repenseai/ tests/
