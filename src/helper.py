import os
import requests


def send_message(chat_id, text, reply_markup=None):
    response_dict = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup:
        response_dict["reply_markup"] = reply_markup

    logging("send_message", response_dict=response_dict)
    req = requests.post(get_url("sendMessage"), json=response_dict)
    logging("send_message", req_json=req.json())
    return req


def edit_message(chat_id, message_id, text, reply_markup=None):
    response_dict = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    }
    if reply_markup:
        response_dict["reply_markup"] = reply_markup

    logging("edit_message", response_dict=response_dict)
    req = requests.post(get_url("editMessageText"), json=response_dict)
    logging("edit_message", req_json=req.json())
    return req


def get_new_group_link():
    req = requests.post(
        get_url("exportChatInviteLink"),
        data={"chat_id": os.environ["TELEGRAM_GROUP_ID"]},
    )
    return req.json()["result"]


def get_url(method):
    return "https://api.telegram.org/bot{}/{}".format(os.environ["TOKEN"], method)


def logging(annotation, **kwargs):
    for k, v in kwargs.items():
        print(annotation, ":", k, "==>", v)


def notify_admin(text):
    for id in get_admin_chat_id():
        send_message(chat_id=id, text=text)


def get_admin_chat_id():
    return [x.strip() for x in os.environ["TELEGRAM_ADMIN"].split(",")]


def fix_reply_markup_readable(reply_markup):
    result = []
    last_text_is_long = False
    for row in reply_markup:
        if len(row["text"]) >= 8:
            result.append([row])
            last_text_is_long = True
        else:
            if (
                len(result) >= 1
                and isinstance(result[-1], list)
                and last_text_is_long == False
            ):
                result[-1].append(row)
            else:
                result.append([row])
            last_text_is_long = False
    return result
