.PHONY: venv install

run-local:
	sam local start-api

build:
	sam build --use-container

# Install Poetry if not available, then install dependencies
setup:
	@command -v poetry >/dev/null 2>&1 || pip install poetry
	poetry install

# Install Poetry if not available, then install with dev dependencies  
setup-dev:
	@command -v poetry >/dev/null 2>&1 || pip install poetry
	poetry install --with dev

run-shell:
	@command -v poetry >/dev/null 2>&1 || pip install poetry
	poetry run python

test:
	@command -v poetry >/dev/null 2>&1 || pip install poetry
	poetry install --with dev
	poetry run pytest tests/unit -v

cleanup:
	sam delete --stack-name "belajarpythonbot"

deploy: build
	sam deploy

test-coverage:
	@command -v poetry >/dev/null 2>&1 || pip install poetry
	poetry install --with dev
	poetry run pytest --cov-report term-missing --cov=src tests/unit

clean:
	rm -rf .venv
	find . -type f -name '*.pyc' -delete