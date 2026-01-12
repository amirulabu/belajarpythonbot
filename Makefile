.PHONY: venv install

run-local:
	sam local start-api

build:
	sam build --use-container

setup:
	poetry install

setup-dev:
	poetry install --with dev

run-shell:
	poetry run python

test: setup-dev
	poetry run pytest tests/unit -v

cleanup:
	sam delete --stack-name "belajarpythonbot"

deploy: build
	sam deploy

test-coverage: setup-dev
	poetry run pytest --cov-report term-missing --cov=src tests/unit

clean:
	rm -rf .venv
	find . -type f -name '*.pyc' -delete