.PHONY: lint
lint:
	black repenseai/ tests/
	flake8 repenseai/ tests/
