import json
from quiz import Quiz

def lambda_handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        quiz = Quiz(body)
        quiz.run()
