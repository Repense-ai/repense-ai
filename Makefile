.PHONY: lint
lint:
	black repenseai/ tests/
	flake8 repenseai/ tests/

test-mcp:
	pytest -s -v --log-cli-level=INFO tests/test_mcp.py
