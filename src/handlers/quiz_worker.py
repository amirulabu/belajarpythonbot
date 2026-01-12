import json
from services.quiz_service import QuizService


def lambda_handler(event, context):
    """Quiz worker Lambda handler - processes messages from SQS."""
    quiz_service = QuizService()
    
    for record in event["Records"]:
        body = json.loads(record["body"])
        quiz_service.handle_telegram_update(body)