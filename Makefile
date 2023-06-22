.PHONY: venv install

VENV=env
PYTHON=$(VENV)/bin/python

run-local:
	sam local start-api

build:
	sam build --use-container

setup-env:
ifeq (,$(wildcard $(VENV)))
	python -m pip install --user virtualenv
	python -m virtualenv env
endif

setup-run: setup-env src/requirements.txt
	$(PYTHON) -m pip install -r src/requirements.txt

run-shell: setup-run
	$(PYTHON) 

setup-test: setup-env tests/requirements.txt
	$(PYTHON) -m pip install -r tests/requirements.txt

test: setup-test
	$(PYTHON) -m PYTHONPATH=src python -m pytest tests/unit -v

cleanup:
	sam delete --stack-name "belajarpythonbot"

deploy: build
	sam deploy

test-coverage: setup-test
	PYTHONPATH=src $(PYTHON) -m pytest --cov-report term-missing --cov=src tests/unit

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete