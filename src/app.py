import json
import os


def lambda_handler(event, context):
    try:
        body = event["body"]
        queryStringParameters = event["queryStringParameters"]

        if queryStringParameters is None:
            raise Exception("No queryStringParameters")

        if queryStringParameters["token"] is None:
            raise Exception("No token provided")

        if queryStringParameters["token"] != os.environ["TOKEN"]:
            raise Exception("Invalid token provided")

        print(body)
        print(queryStringParameters)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "success!",
                }
            ),
        }

    except:
        print("An exception occurred")
        print(context)
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": "An exception occurred",
                }
            ),
        }
