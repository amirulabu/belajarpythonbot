# belajarpythonbot

This repo is for a telegram bot acting as a gatekeeper to enter telegram group Belajar Python. This group is for Malay speaking audience who are interested to learn and share about Python programming language.

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- hello_world - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Commands

- `make test` install testing packages and run test
- `make deploy` build and deploy

## Chat filtering (stop replying in groups)

By default, the bot responds **everywhere except Telegram groups/supergroups**.

If you want to allow the bot to respond only in a specific chat (for example, a specific channel or group), set:

- `TELEGRAM_ALLOWED_CHAT_IDS`: comma-separated list of allowed chat IDs (supports negative IDs), e.g. `-1001234567890`

## Tips

### Run only one test

- `PYTHONPATH=src python -m pytest tests/unit/test_helper.py -sv -k "fix_reply"` this command will run the test inside file `test_helper.py` with the text `fix_reply`
