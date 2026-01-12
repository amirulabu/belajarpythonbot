import os
import boto3
from datetime import datetime
from typing import Dict, Any, List, Optional
from boto3.dynamodb.conditions import Key
from utils import (
    parse_telegram_update,
    parse_callback_data,
    get_full_name,
    is_correct_answer,
    build_reply_markup,
)
from telegram_service import TelegramService


class QuizService:
    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")  
        self.table = dynamodb.Table("belajarpythonbot2023")  # type: ignore
        self.dynamodb = dynamodb
        self.telegram_service = TelegramService()
        self.quiz_data = self._load_quiz_data()

    def handle_telegram_update(self, data: Dict[str, Any]) -> None:
        """Handle incoming Telegram update."""
        message, callback_query = parse_telegram_update(data)

        if message and message["text"] == "/start":
            self._handle_start_command(message)
        elif callback_query:
            self._handle_callback_query(callback_query)
        elif message:
            self._handle_text_message(message)

    def _handle_start_command(self, message: Dict[str, Any]) -> None:
        """Handle /start command."""
        if message["chat_id"] <= 0:  # Ignore group chats
            return

        user = self._add_or_get_user(
            message["user_id"], message["first_name"], message["username"]
        )

        # Send welcome message
        self.telegram_service.send_message(
            chat_id=message["chat_id"],
            text=f"Hello {get_full_name(user['first_name'], user.get('last_name'))}, please answer the following questions",
        )

        # Send first question
        self._send_question(message["chat_id"], 0)

        # Notify admin
        full_name = get_full_name(message["first_name"], message.get("last_name"))
        username = message.get("username", "")
        self.telegram_service.notify_admins(
            f"{full_name} - {username} started the quiz"
        )

    def _handle_callback_query(self, callback_query: Dict[str, Any]) -> None:
        """Handle callback query from inline buttons."""
        question_index, answer = parse_callback_data(callback_query["data"])

        if question_index < 0:
            return

        # Check answer
        current_question = self.quiz_data[question_index]
        is_correct = is_correct_answer(current_question, answer)

        # Save result
        self._save_quiz_result(callback_query["user_id"], question_index, is_correct)

        # Remove inline button by editing the message
        if callback_query.get("message_id") and callback_query.get("message_text"):
            self.telegram_service.edit_message(
                chat_id=callback_query["chat_id"],
                message_id=callback_query["message_id"],
                text=callback_query["message_text"],
            )

        # Move to next question
        next_question_index = question_index + 1

        if next_question_index < len(self.quiz_data):
            self._send_question(callback_query["chat_id"], next_question_index)
        else:
            self._send_quiz_results(
                callback_query["chat_id"], callback_query["user_id"]
            )

    def _handle_text_message(self, message: Dict[str, Any]) -> None:
        """Handle regular text messages."""
        self.telegram_service.send_message(
            chat_id=message["chat_id"], text=f"Echo, {message['text']}"
        )

    def _send_question(self, chat_id: int, question_index: int) -> None:
        """Send a quiz question to the user."""
        if question_index >= len(self.quiz_data):
            return

        question = self.quiz_data[question_index]
        reply_markup = build_reply_markup(question["choices"], question_index)

        self.telegram_service.send_message(
            chat_id=chat_id, text=question["question"], reply_markup=reply_markup
        )

    def _send_quiz_results(self, chat_id: int, user_id: int) -> None:
        """Send quiz results to the user."""
        correct_count = self._get_correct_answer_count(user_id)
        total_questions = len(self.quiz_data)

        self.telegram_service.send_message(
            chat_id=chat_id,
            text=f"You have answered {correct_count} questions correctly",
        )

        if correct_count == total_questions:
            group_link = self._get_group_link()
            self.telegram_service.send_message(
                chat_id=chat_id,
                text=f"Congratulations, you have answered all questions correctly\nJoin the group with this link {group_link}",
            )
        else:
            self.telegram_service.send_message(
                chat_id=chat_id, text="Sorry, please try again. Click here /start"
            )

    def _load_quiz_data(self) -> List[Dict[str, Any]]:
        """Load quiz data from quiz_dict module."""
        from services.quiz_dict import quiz_dict

        return quiz_dict

    def _add_or_get_user(
        self, user_id: int, first_name: str, username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add user to database or get existing user."""
        try:
            user_db = self.table.get_item(Key={"UserID": user_id})["Item"]
            return user_db
        except KeyError:
            self.table.put_item(
                Item={
                    "UserID": user_id,
                    "first_name": first_name,
                    "username": username,
                    "question": {},
                }
            )
            return self.table.get_item(Key={"UserID": user_id})["Item"]

    def _save_quiz_result(
        self, user_id: int, question_index: int, is_correct: bool
    ) -> None:
        """Save quiz result to database."""
        result = "correct" if is_correct else "wrong"
        try:
            self.table.update_item(
                Key={"UserID": user_id},
                UpdateExpression="SET question.#question = :res",
                ExpressionAttributeNames={"#question": f"Q{question_index}"},
                ExpressionAttributeValues={":res": result},
            )
        except KeyError:
            pass  # User not found

    def _get_correct_answer_count(self, user_id: int) -> int:
        """Get count of correct answers for a user."""
        try:
            user_db = self.table.get_item(Key={"UserID": user_id})["Item"]
            counter = 0
            questions = user_db["question"]
            for result in questions.values():
                if result == "correct":
                    counter += 1
            return counter
        except KeyError:
            return 0

    def _get_group_link(self) -> str:
        """Get or generate group invite link."""
        try:
            link_db = self.table.get_item(Key={"UserID": -9999})["Item"]

            # Check if link is still valid (5 minutes)
            if link_db["expiry"] + 300 > round(datetime.now().timestamp()):
                return link_db["group_link"]
            else:
                new_link = self.telegram_service.get_new_group_link()
                self._save_group_link(new_link)
                return new_link
        except:
            new_link = self.telegram_service.get_new_group_link()
            self._save_group_link(new_link)
            return new_link

    def _save_group_link(self, group_link: str) -> None:
        """Save group link to database."""
        self.table.put_item(
            Item={
                "UserID": -9999,
                "expiry": round(datetime.now().timestamp()),
                "group_link": group_link,
            }
        )
