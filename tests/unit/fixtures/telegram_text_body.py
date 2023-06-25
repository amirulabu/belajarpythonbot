import pytest


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


@pytest.fixture()
def telegram_text_body_start_command():
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
            "text": "/start",
            "entities": [
                {
                    "offset": 0,
                    "length": 6,
                    "type": "bot_command",
                },
            ],  # https://core.telegram.org/bots/api#messageentity
        },
    }
