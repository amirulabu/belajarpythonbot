import requests
from src.helper import get_admin_chat_id, get_url, logging, notify_admin, send_message

import src.helper
import builtins


def test_send_message(mocker, monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    telegram_url = "https://api.telegram.org/bot12345/sendMessage"
    monkeypatch.setattr(src.helper, "send_message", telegram_url)
    spy = mocker.spy(requests, "post")
    send_message(chat_id="12345", text="test")
    spy.assert_called_once_with(telegram_url, json={"chat_id": "12345", "text": "test"})


def test_send_message_with_reply_markup(mocker, monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    telegram_url = "https://api.telegram.org/bot12345/sendMessage"
    monkeypatch.setattr(src.helper, "send_message", telegram_url)
    spy = mocker.spy(requests, "post")
    send_message(chat_id="12345", text="test", reply_markup={"keyboard": "test"})
    spy.assert_called_once_with(
        telegram_url,
        json={"chat_id": "12345", "text": "test", "reply_markup": {"keyboard": "test"}},
    )


def test_get_url(monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    ret = get_url("sendMessage")
    assert ret == "https://api.telegram.org/bot12345/sendMessage"


def test_logging(monkeypatch, mocker):
    monkeypatch.setattr(builtins, "print", lambda *args: None)
    spy = mocker.spy(builtins, "print")
    logging("test logging", test="test")
    spy.assert_called_with("test logging", ":", "test", "==>", "test")
    mocker.stopall()


def test_logging_multiple(monkeypatch, mocker):
    monkeypatch.setattr(builtins, "print", lambda *args: None)
    spy = mocker.spy(builtins, "print")
    logging("test logging", test="test", test2="test2")
    assert spy.call_count == 2
    spy.assert_any_call("test logging", ":", "test", "==>", "test")
    spy.assert_any_call("test logging", ":", "test2", "==>", "test2")


def test_notify_admin(mocker, monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    monkeypatch.setenv("TELEGRAM_ADMIN", "12345")
    spy = mocker.spy(src.helper, "send_message")
    notify_admin(text="test")
    spy.assert_called_once_with(chat_id="12345", text="test")


def test_notify_multiple_admin(mocker, monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    monkeypatch.setenv("TELEGRAM_ADMIN", "12345, 54321")
    spy = mocker.spy(src.helper, "send_message")
    notify_admin(text="test")
    spy.assert_any_call(chat_id="12345", text="test")
    spy.assert_any_call(chat_id="54321", text="test")


def test_get_admin_chat_id(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ADMIN", "12345")
    ret = get_admin_chat_id()
    assert ret == ["12345"]


def test_get_multiple_admin_chat_id(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ADMIN", "12345, 54321")
    ret = get_admin_chat_id()
    assert ret == ["12345", "54321"]