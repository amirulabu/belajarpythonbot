import json
import os
from services.quiz_service import QuizService
from errors import EnvironmentException, UnauthorizedException


def lambda_handler(event, context):
    """Quiz worker Lambda handler - processes messages from SQS."""
    quiz_service = QuizService()

    # Validate environment variables
    _validate_environment()

    print("Received event:", json.dumps(event))

    try:

        for record in event["Records"]:
            body = json.loads(record["body"])
            quiz_service.handle_telegram_update(body)

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


def _validate_environment():
    """Validate required environment variables."""
    required_vars = ["TOKEN", "TELEGRAM_ADMIN", "TELEGRAM_GROUP_ID"]

    for var in required_vars:
        if var not in os.environ:
            raise EnvironmentException(f"{var} environment variable is not set")
