import os
import requests
from typing import List, Optional, Dict, Any, Union


class TelegramService:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.admin_ids = [id.strip() for id in os.getenv("TELEGRAM_ADMIN", "").split(",")]
    
    def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> requests.Response:
        """Send a message to Telegram chat."""
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        self._log("send_message", payload=payload)
        response = requests.post(self._get_url("sendMessage"), json=payload)
        self._log("send_message", response_json=response.json())
        return response
    
    def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None) -> requests.Response:
        """Edit an existing message."""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        self._log("edit_message", payload=payload)
        response = requests.post(self._get_url("editMessageText"), json=payload)
        self._log("edit_message", response_json=response.json())
        return response
    
    def notify_admins(self, text: str) -> None:
        """Send notification to all admin users."""
        for admin_id in self.admin_ids:
            if admin_id:  # Skip empty admin IDs
                self.send_message(chat_id=int(admin_id), text=text)
    
    def get_new_group_link(self) -> str:
        """Generate new group invite link."""
        response = requests.post(
            self._get_url("exportChatInviteLink"),
            data={"chat_id": os.getenv("TELEGRAM_GROUP_ID")}
        )
        return response.json()["result"]
    
    def _get_url(self, method: str) -> str:
        """Get Telegram API URL for a method."""
        return f"https://api.telegram.org/bot{self.token}/{method}"
    
    def _log(self, annotation: str, **kwargs) -> None:
        """Log API calls and responses."""
        for k, v in kwargs.items():
            print(f"{annotation}: {k} ==> {v}")