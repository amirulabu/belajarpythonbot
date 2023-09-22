import pytest


@pytest.fixture()
def telegram_callback_query_body():
    return {
        "update_id": 9999999999,
        "callback_query": {
            "id": "7999999999999990",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "John",
                "last_name": "Doe",
                "username": "JohnDoe",
                "language_code": "en",
            },
            "message": {
                "message_id": 1111,
                "from": {
                    "id": 321321,
                    "is_bot": True,
                    "first_name": "test_bot",
                    "username": "test_bot",
                },
                "chat": {
                    "id": 12345,
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "JohnDoe",
                    "type": "private",
                },
                "date": 1687615941,
                "text": "Siapakah yang mencipta Python?",
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Guido van Rossum",
                                "callback_data": "0#Guido van Rossum",
                            },
                            {"text": "Google", "callback_data": "0#Google"},
                            {"text": "Matz", "callback_data": "0#Matz"},
                            {
                                "text": "Dennis Ritchie",
                                "callback_data": "0#Dennis Ritchie",
                            },
                        ]
                    ]
                },
            },
            "chat_instance": "-49999999999",
            "data": "0#Guido van Rossum",
        },
    }
