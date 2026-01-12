from typing import Dict, Any, Optional, Tuple


def parse_telegram_update(data: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
    """Parse Telegram update into message and callback_query dictionaries."""
    message = data.get("message")
    callback_query = data.get("callback_query")
    
    if message:
        # Extract message fields
        parsed_message = {
            "text": message.get("text", ""),
            "chat_id": message["chat"]["id"],
            "user_id": message["from"]["id"],
            "first_name": message["from"]["first_name"],
            "last_name": message["from"].get("last_name"),
            "username": message["from"].get("username")
        }
        return parsed_message, None
    
    if callback_query:
        # Extract callback query fields
        parsed_callback = {
            "data": callback_query["data"],
            "chat_id": callback_query["from"]["id"],
            "user_id": callback_query["from"]["id"],
            "first_name": callback_query["from"]["first_name"],
            "last_name": callback_query["from"].get("last_name"),
            "username": callback_query["from"].get("username"),
            "message_id": callback_query.get("message", {}).get("message_id"),
            "message_text": callback_query.get("message", {}).get("text"),
            "chat_instance": callback_query.get("chat_instance"),
            "is_bot": callback_query["from"].get("is_bot")
        }
        return None, parsed_callback
    
    return None, None


def parse_callback_data(callback_data: str) -> Tuple[int, str]:
    """Parse callback data into question_index and answer."""
    try:
        question_index, answer = callback_data.split('#', 1)
        return int(question_index), answer
    except (ValueError, IndexError):
        return -1, ""


def get_full_name(first_name: str, last_name: Optional[str] = None) -> str:
    """Get full name from first and last name."""
    return f"{first_name} {last_name}" if last_name else first_name


def is_correct_answer(question: Dict[str, Any], answer: str) -> bool:
    """Check if answer matches the correct answer for a question."""
    return answer == question["answer"]


def build_reply_markup(choices: list, question_index: int) -> Dict[str, Any]:
    """Build reply markup for quiz question."""
    buttons = []
    for choice in choices:
        buttons.append({
            "text": choice,
            "callback_data": f"{question_index}#{choice}"
        })
    
    return {"inline_keyboard": format_reply_markup(buttons)}


def format_reply_markup(reply_markup: list) -> list:
    """Format reply markup for better readability on Telegram."""
    result = []
    last_text_is_long = False
    
    for row in reply_markup:
        if len(row["text"]) >= 8:
            result.append([row])
            last_text_is_long = True
        else:
            if result and isinstance(result[-1], list) and not last_text_is_long:
                result[-1].append(row)
            else:
                result.append([row])
            last_text_is_long = False
    
    return result