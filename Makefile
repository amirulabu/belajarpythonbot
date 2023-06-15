.PHONY: run clean

run:
	sam local start-api

build:
	sam build --use-container

setup-test: tests/requirements.txt
	pip install -r tests/requirements.txt --user

test: setup-test
	python -m pytest tests/unit -v

cleanup:
	sam delete --stack-name "belajarpythonbot"

deploy: build
	sam deploy --guided