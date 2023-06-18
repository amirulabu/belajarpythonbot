from db_operation import UserDDB
from helper import send_message
from quiz_dict import quiz_dict
from helper import edit_message, notify_admin


class Quiz:
    """Loads quiz and holds the logic for the quiz"""

    def __init__(self, body):
        self.message = body.get("message")
        self.question_index = 0
        self.text = ""
        if self.message:
            self.text = body.get("message").get("text")
            self.chat_id = body.get("message").get("chat").get("id")
            self.user_id = body.get("message").get("from").get("id")
            self.first_name = body.get("message").get("from").get("first_name")
            # Telegram allow accounts without last name
            self.last_name = body.get("message").get("from").get("last_name")
            self.username = body.get("message").get("from").get("username")

        self.callback_query = body.get("callback_query")
        if self.callback_query:
            # The user submit the answer to the quiz via inline button
            self.inline_button = body.get("callback_query").get("data")
            self.question_index = int(
                body.get("callback_query").get("data").split("#")[0]
            )
            self.answer = body.get("callback_query").get("data").split("#")[1]
            self.chat_id = body.get("callback_query").get("from").get("id")
            self.user_id = body.get("callback_query").get("from").get("id")
            self.first_name = body.get("callback_query").get("from").get("first_name")
            # Telegram allow accounts without last name
            self.last_name = body.get("callback_query").get("from").get("last_name")
            # Telegram allow accounts without username
            self.username = body.get("callback_query").get("from").get("username")
            self.is_bot = body.get("callback_query").get("from").get("is_bot")
            self.chat_instance = body.get("callback_query").get("chat_instance")
            self.message_id = (
                body.get("callback_query").get("message").get("message_id")
            )
            self.message_text = body.get("callback_query").get("message").get("text")

        self.questions = quiz_dict

    def run(self):
        """Logic on what to reply"""
        UserDDB.add_or_get_user(self.user_id, self.first_name, self.username)
        if self.text == "/start":
            self.welcome()
            self.send_question()
            self.notify_admin_start_quiz()
        elif self.callback_query:
            result = self.check_answer()
            self.remove_inline_button()
            self.save_answer(result)
            self.question_index += 1
            self.send_question()
            if self.question_index == len(self.questions):
                self.send_results()
        else:
            self.echo_message()

    def echo_message(self):
        send_message(
            chat_id=self.chat_id,
            text=f"Echo, {self.text}",
        )

    def get_correct_answer(self):
        return self.questions[self.question_index]["answer"]

    def check_answer(self):
        if self.answer == self.get_correct_answer():
            return True
        return False

    def save_answer(self, result):
        UserDDB.add_result(self.user_id, self.question_index, result)

    def send_results(self):
        correct_count = UserDDB.get_result(self.user_id)
        send_message(
            chat_id=self.chat_id,
            text=f"You have answered {correct_count} questions correctly",
        )
        if correct_count == len(self.questions):
            group_link = UserDDB.get_group_link()
            send_message(
                chat_id=self.chat_id,
                text=f"Congratulations, you have answered all questions correctly\nJoin the group with this link {group_link}",
            )
        else:
            send_message(
                chat_id=self.chat_id,
                text=f"Sorry, please try again. Click here /start",
            )

    def full_name(self):
        return (
            "{} {}".format(self.first_name, self.last_name)
            if self.last_name
            else "{}".format(self.first_name)
        )

    def welcome(self):
        send_message(
            chat_id=self.chat_id,
            text=f"Hello {self.full_name()}, please answer the following questions",
        )

    def parse_reply_markup(self):
        """Parse the reply markup from the quiz_dict"""
        reply_markup = []
        for choice in self.questions[self.question_index]["choices"]:
            reply_markup.append(
                {
                    "text": choice,
                    "callback_data": f"{self.question_index}#{choice}",
                }
            )
        return {"inline_keyboard": [reply_markup]}

    def send_question(self):
        if self.question_index >= len(self.questions):
            return
        send_message(
            chat_id=self.chat_id,
            text=self.questions[self.question_index]["question"],
            reply_markup=self.parse_reply_markup(),
        )

    def remove_inline_button(self):
        edit_message(
            chat_id=self.chat_id, message_id=self.message_id, text=self.message_text
        )

    def notify_admin_start_quiz(self):
        notify_admin(f"{self.full_name() - self.username} started the quiz")
