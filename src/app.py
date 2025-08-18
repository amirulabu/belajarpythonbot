import json
import os
import traceback
import boto3

from errors import EnvironmentException, UnauthorizedException
from quiz import Quiz
from helper import logging


def lambda_handler(event, context):
    try:
        if "TOKEN" not in os.environ:
            raise EnvironmentException("TOKEN environment variable is not set")

        if "TELEGRAM_ADMIN" not in os.environ:
            raise EnvironmentException("TELEGRAM_ADMIN environment variable is not set")

        if "TELEGRAM_GROUP_ID" not in os.environ:
            raise EnvironmentException(
                "TELEGRAM_GROUP_ID environment variable is not set"
            )

        body = event["body"]
        queryStringParameters = event["queryStringParameters"]

        if "token" not in queryStringParameters:
            raise UnauthorizedException("No token provided")

        if queryStringParameters["token"] != os.environ["TOKEN"]:
            raise UnauthorizedException("Invalid token provided")

        sqs = boto3.client("sqs")
        queue_url = os.environ["QUIZ_QUEUE_URL"]
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=body
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "success!",
                },
            ),
        }

    except UnauthorizedException as e:
        return {
            "statusCode": 401,
            "body": json.dumps(
                {
                    "error": {
                        "message": str(e),
                    },
                },
            ),
        }

    except Exception as e:
        print(e)
        print(context)
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": {
                        "message": "An exception occurred",
                    },
                },
            ),
        }
