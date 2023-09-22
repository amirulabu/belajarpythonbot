import requests
from src.helper import (
    edit_message,
    fix_reply_markup_readable,
    get_admin_chat_id,
    get_new_group_link,
    get_url,
    logging,
    notify_admin,
    send_message,
)

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


def test_edit_message(mocker, monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    spy_logging = mocker.spy(src.helper, "logging")
    spy_requests_post = mocker.spy(requests, "post")
    edit_message(chat_id="12345", message_id="12345", text="test")
    assert spy_logging.call_count == 2
    assert spy_requests_post.call_count == 1
    spy_logging.assert_any_call(
        "edit_message",
        response_dict={"chat_id": "12345", "message_id": "12345", "text": "test"},
    )
    spy_requests_post.assert_called_once_with(
        "https://api.telegram.org/bot12345/editMessageText",
        json={"chat_id": "12345", "message_id": "12345", "text": "test"},
    )


def test_edit_message_with_reply_markup(mocker, monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    spy_logging = mocker.spy(src.helper, "logging")
    spy_requests_post = mocker.spy(requests, "post")
    edit_message(
        chat_id="12345",
        message_id="12345",
        text="test",
        reply_markup={"keyboard": "test"},
    )
    assert spy_logging.call_count == 2
    assert spy_requests_post.call_count == 1
    spy_logging.assert_any_call(
        "edit_message",
        response_dict={
            "chat_id": "12345",
            "message_id": "12345",
            "text": "test",
            "reply_markup": {"keyboard": "test"},
        },
    )
    spy_requests_post.assert_called_once_with(
        "https://api.telegram.org/bot12345/editMessageText",
        json={
            "chat_id": "12345",
            "message_id": "12345",
            "text": "test",
            "reply_markup": {"keyboard": "test"},
        },
    )


def test_fix_reply_markup_readable_short_text():
    result = fix_reply_markup_readable(
        [
            {"text": "test", "callback_data": "test1"},
        ]
    )
    assert result == [
        {"text": "test", "callback_data": "test1"},
    ]


def test_fix_reply_markup_readable_short_and_long_text():
    result = fix_reply_markup_readable(
        [
            {"text": "test1", "callback_data": "test1"},
            {"text": "test2", "callback_data": "test2"},
            {"text": "a long text3", "callback_data": "test3"},
            {"text": "a long text4", "callback_data": "test4"},
        ]
    )
    assert result == [
        {"text": "test1", "callback_data": "test1"},
        {"text": "test2", "callback_data": "test2"},
        [
            {"text": "a long text3", "callback_data": "test3"},
        ],
        [
            {"text": "a long text4", "callback_data": "test4"},
        ],
    ]


def test_fix_reply_markup_readable_long_text():
    result = fix_reply_markup_readable(
        [
            {"text": "a long text1", "callback_data": "test1"},
            {"text": "a long text2", "callback_data": "test2"},
            {"text": "a long text3", "callback_data": "test3"},
            {"text": "a long text4", "callback_data": "test4"},
        ]
    )
    assert result == [
        [
            {"text": "a long text1", "callback_data": "test1"},
        ],
        [
            {"text": "a long text2", "callback_data": "test2"},
        ],
        [
            {"text": "a long text3", "callback_data": "test3"},
        ],
        [
            {"text": "a long text4", "callback_data": "test4"},
        ],
    ]


class MockResponse:
    # mock json() method always returns a specific testing dictionary
    @staticmethod
    def json():
        return {"result": "http://mock_group_link"}


def test_get_new_group_link(monkeypatch):
    monkeypatch.setenv("TOKEN", "12345")
    monkeypatch.setenv("TELEGRAM_GROUP_ID", "-12345")

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "post", mock_post)

    group_link = get_new_group_link()
    assert group_link == "http://mock_group_link"
