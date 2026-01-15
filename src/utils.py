import os
from typing import Dict, Any, Optional, Tuple, Set


def parse_telegram_update(data: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[Dict]]:
    """Parse Telegram update into message and callback_query dictionaries."""
    message = data.get("message")
    callback_query = data.get("callback_query")
    
    if message:
        chat = message.get("chat", {}) or {}
        chat_id = chat.get("id")
        chat_type = chat.get("type")
        if chat_type is None and isinstance(chat_id, int):
            # Telegram chat IDs are typically >0 for private chats and <0 for groups/channels.
            chat_type = "private" if chat_id > 0 else "group"

        from_user = message.get("from") or {}
        # Extract message fields
        parsed_message = {
            "text": message.get("text", ""),
            "chat_id": chat_id,
            "chat_type": chat_type,
            "user_id": from_user.get("id"),
            "first_name": from_user.get("first_name"),
            "last_name": from_user.get("last_name"),
            "username": from_user.get("username"),
        }
        return parsed_message, None
    
    if callback_query:
        cq_message = callback_query.get("message", {}) or {}
        cq_chat = cq_message.get("chat", {}) or {}
        cq_chat_id = cq_chat.get("id") or callback_query.get("from", {}).get("id")
        cq_chat_type = cq_chat.get("type")
        if cq_chat_type is None and isinstance(cq_chat_id, int):
            cq_chat_type = "private" if cq_chat_id > 0 else "group"

        # Extract callback query fields
        parsed_callback = {
            "data": callback_query["data"],
            "chat_id": cq_chat_id,
            "chat_type": cq_chat_type,
            "user_id": callback_query["from"]["id"],
            "first_name": callback_query["from"]["first_name"],
            "last_name": callback_query["from"].get("last_name"),
            "username": callback_query["from"].get("username"),
            "message_id": cq_message.get("message_id"),
            "message_text": cq_message.get("text"),
            "chat_instance": callback_query.get("chat_instance"),
            "is_bot": callback_query["from"].get("is_bot")
        }
        return None, parsed_callback
    
    return None, None


def get_allowed_chat_ids() -> Set[int]:
    """
    Parse TELEGRAM_ALLOWED_CHAT_IDS env var into a set of chat IDs.

    Format: comma-separated integers (supports negative IDs).
    Example: "-1001234567890,123456"
    """
    raw = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    if not raw:
        return set()

    allowed: Set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            allowed.add(int(part))
        except ValueError:
            # Ignore invalid entries rather than crashing the bot.
            continue
    return allowed


def is_allowed_chat(chat_id: Optional[int], chat_type: Optional[str]) -> bool:
    """
    Decide whether the bot should respond to an update from this chat.

    - If TELEGRAM_ALLOWED_CHAT_IDS is set: only allow those chat IDs.
    - Otherwise: allow everywhere except Telegram groups/supergroups.
    """
    allowed_ids = get_allowed_chat_ids()
    if allowed_ids:
        return isinstance(chat_id, int) and chat_id in allowed_ids

    return chat_type not in {"group", "supergroup"}


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