import pytest

# from tests.unit.fixtures import telegram_text_body
from src.quiz import Quiz


@pytest.fixture()
def telegram_text_body():
    return {
        "update_id": 9999999999,
        "message": {
            "message_id": 1234,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "John",
                "last_name": "Doe",
                "username": "JohnDoe",
                "language_code": "en",
            },
            "chat": {
                "id": 12345,
                "first_name": "John",
                "last_name": "Doe",
                "username": "JohnDoe",
                "type": "private",
            },
            "date": 1687615926,
            "text": "Test message from a telegram user",
        },
    }


def test_quiz_text(telegram_text_body):
    quiz = Quiz(telegram_text_body)
    assert quiz.text == telegram_text_body.get("message").get("text")
