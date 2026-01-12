import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.quiz_service import QuizService
from src.telegram_service import TelegramService


@pytest.fixture
def quiz_service():
    with patch('src.services.quiz_service.boto3') as mock_boto3:
        # Mock DynamoDB setup
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.resource.return_value = mock_dynamodb
        
        with patch('src.telegram_service.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'TOKEN': 'test_token',
                'TELEGRAM_ADMIN': '12345,67890'
            }.get(key, default)
            
            return QuizService()


@pytest.fixture
def telegram_update_start():
    return {
        "message": {
            "message_id": 1234,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "John",
                "last_name": "Doe",
                "username": "JohnDoe",
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
        },
    }


@pytest.fixture
def telegram_update_callback():
    return {
        "callback_query": {
            "id": "12345",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "John",
                "last_name": "Doe",
                "username": "JohnDoe",
            },
            "message": {
                "message_id": 678,
                "date": 1687615926,
                "text": "What is 2+2?",
            },
            "chat_instance": "123456789",
            "data": "0#4",
        },
    }


def test_parse_telegram_update_message(telegram_update_start):
    from src.utils import parse_telegram_update
    
    message, callback_query = parse_telegram_update(telegram_update_start)
    
    assert message is not None
    assert message["text"] == "/start"
    assert message["chat_id"] == 12345
    assert message["first_name"] == "John"
    assert message["last_name"] == "Doe"
    assert message["username"] == "JohnDoe"
    assert callback_query is None


def test_parse_telegram_update_callback(telegram_update_callback):
    from src.utils import parse_telegram_update
    
    message, callback_query = parse_telegram_update(telegram_update_callback)
    
    assert callback_query is not None
    assert callback_query["data"] == "0#4"
    assert callback_query["chat_id"] == 12345
    assert callback_query["message_id"] == 678
    assert message is None


def test_parse_callback_data():
    from src.utils import parse_callback_data
    
    question_index, answer = parse_callback_data("0#Option A")
    assert question_index == 0
    assert answer == "Option A"


def test_is_correct_answer():
    from src.utils import is_correct_answer
    
    question = {"question": "Test", "choices": ["A", "B"], "answer": "A"}
    
    assert is_correct_answer(question, "A") is True
    assert is_correct_answer(question, "B") is False


def test_build_reply_markup():
    from src.utils import build_reply_markup
    
    choices = ["Option A", "Option B"]
    markup = build_reply_markup(choices, 0)
    
    assert "inline_keyboard" in markup
    buttons = markup["inline_keyboard"]
    assert len(buttons) >= 1  # May be 1 or 2 rows based on formatting
    
    # Extract all buttons to check content
    all_buttons = []
    for row in buttons:
        all_buttons.extend(row)
    
    texts = [btn["text"] for btn in all_buttons]
    data = [btn["callback_data"] for btn in all_buttons]
    
    assert "Option A" in texts
    assert "Option B" in texts
    assert "0#Option A" in data
    assert "0#Option B" in data


@patch('src.telegram_service.requests.post')
def test_telegram_service_send_message(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response
    
    service = TelegramService()
    
    with patch('src.telegram_service.os.getenv') as mock_getenv:
        mock_getenv.return_value = 'test_token'
        service.send_message(12345, "Hello")
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "sendMessage" in args[0]
    assert kwargs["json"]["chat_id"] == 12345
    assert kwargs["json"]["text"] == "Hello"


def test_quiz_service_handle_start_command(quiz_service, telegram_update_start):
    with patch.object(quiz_service.telegram_service, 'send_message') as mock_send:
        quiz_service.handle_telegram_update(telegram_update_start)
        
        # Should call send_message for welcome message
        mock_send.assert_called()
        
        # Check that calls include welcome message
        call_args = mock_send.call_args_list
        welcome_text_found = any(
            "Hello" in str(call.kwargs.get('text', '')) 
            for call in call_args
        )
        assert welcome_text_found


def test_quiz_service_handle_callback_query(quiz_service, telegram_update_callback):
    with patch.object(quiz_service.telegram_service, 'send_message') as mock_send, \
         patch.object(quiz_service.telegram_service, 'edit_message') as mock_edit, \
         patch.object(quiz_service, '_save_quiz_result') as mock_save:
        
        quiz_service.handle_telegram_update(telegram_update_callback)
        
        mock_save.assert_called_once()
        mock_edit.assert_called_once()
        
        # Verify the result was saved
        save_args = mock_save.call_args[0]
        assert save_args[0] == 12345  # user_id
        assert save_args[1] == 0      # question_index


def test_quiz_service_handle_text_message(quiz_service):
    text_update = {
        "message": {
            "from": {"id": 12345, "first_name": "John"},
            "chat": {"id": 12345},
            "text": "Hello world"
        }
    }
    
    with patch.object(quiz_service.telegram_service, 'send_message') as mock_send:
        quiz_service.handle_telegram_update(text_update)
        
        mock_send.assert_called_once_with(chat_id=12345, text="Echo, Hello world")