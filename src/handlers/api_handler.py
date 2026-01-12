import os
import json
import boto3
from services.quiz_service import QuizService
from errors import EnvironmentException, UnauthorizedException


def lambda_handler(event, context):
    """Main API Gateway Lambda handler."""
    try:

        # Validate request token
        _validate_request_token(event)

        # Queue the message for processing
        sqs = boto3.client("sqs")
        queue_url = os.environ["QUIZ_QUEUE_URL"]
        body = event.get("body", "")

        print("Queueing message to SQS:", body)

        sqs.send_message(QueueUrl=queue_url, MessageBody=body)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "success!"}),
        }

    except UnauthorizedException as e:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": {"message": str(e)}}),
        }

    except Exception as e:
        import traceback

        print(e)
        print(context)
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": json.dumps({"error": {"message": "An exception occurred"}}),
        }


def _validate_request_token(event):
    """Validate request token in query parameters."""
    query_params = event.get("queryStringParameters", {})

    if "token" not in query_params:
        raise UnauthorizedException("No token provided")

    if query_params["token"] != os.environ["TOKEN"]:
        raise UnauthorizedException("Invalid token provided")
