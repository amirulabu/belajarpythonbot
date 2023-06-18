import boto3
from datetime import datetime

from helper import get_new_group_link


dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

table = dynamodb.Table("belajarpythonbot2023")  # type: ignore


CONFIG = {
    "group_link_UserID": -9999,
    "group_link_expiry": 300,
}


class UserDDB:
    @staticmethod
    def add_or_get_user(user_id, first_name, username=None):
        # takes the user object and if the user is in the db, returns the information about user from db
        # if the user is not in the db, push user info to db and returns the user from db
        try:
            user_db = table.get_item(Key={"UserID": user_id})["Item"]
            return user_db
        except KeyError:
            table.put_item(
                Item={
                    "UserID": user_id,
                    "first_name": first_name,
                    "username": username,
                    "question": {},
                }
            )
            return table.get_item(Key={"UserID": user_id})["Item"]

    @staticmethod
    def get_result(user_id):
        # check how much correct questions answered
        try:
            user_db = table.get_item(Key={"UserID": user_id})["Item"]
            counter = 0
            question = user_db["question"]
            for r in question.values():
                if r == "correct":
                    counter = counter + 1
            return counter

        except KeyError:
            return "User is not in db"

    @staticmethod
    def add_result(user_id, question_index, isCorrect):
        result = "correct" if isCorrect else "wrong"
        try:
            table.update_item(
                Key={"UserID": user_id},
                UpdateExpression="SET question.#question = :res",
                ExpressionAttributeNames={"#question": f"Q{question_index}"},
                ExpressionAttributeValues={":res": result},
            )
        except KeyError:
            return "User is not in db"

    @staticmethod
    def get_group_link():
        try:
            link_db = table.get_item(
                Key={
                    "UserID": CONFIG.get("group_link_UserID"),
                }
            )["Item"]
            # if expiry timestamp is less than 5 minutes ago
            if link_db["expiry"] + 300 > round(datetime.now().timestamp()):
                return link_db["group_link"]
            else:
                new_link = get_new_group_link()
                UserDDB.save_group_link(new_link)
                return new_link

        except:
            new_link = get_new_group_link()
            UserDDB.save_group_link(new_link)
            return new_link

    @staticmethod
    def save_group_link(group_link):
        table.put_item(
            Item={
                "UserID": CONFIG.get("group_link_UserID"),
                "expiry": round(datetime.now().timestamp()),
                "group_link": group_link,
            }
        )
