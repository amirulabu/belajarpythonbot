.PHONY: run clean

run-local:
	sam local start-api

build:
	sam build --use-container

setup-run: src/requirements.txt
	pip install -r src/requirements.txt --user

run-shell: setup-run
	python 

setup-test: tests/requirements.txt
	pip install -r tests/requirements.txt --user

test: setup-test
	PYTHONPATH=src python -m pytest tests/unit -v

cleanup:
	sam delete --stack-name "belajarpythonbot"

deploy: build
	sam deploy

test-coverage: setup-test
	PYTHONPATH=src python -m pytest --cov-report term-missing --cov=src tests/unit