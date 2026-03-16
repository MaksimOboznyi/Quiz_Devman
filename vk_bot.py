import os
import random

import redis
import vk_api
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll


def get_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def send_message(user_id, text):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=0,
        keyboard=get_keyboard(),
    )


def clean_answer(answer):
    answer = answer.split(".")[0]
    answer = answer.split("(")[0]
    return answer.strip().lower()


def main():
    load_dotenv()

    vk_token = os.getenv("VK_BOT_TOKEN")
    redis_url = os.getenv("REDIS_URL")
    questions_path = os.getenv("QUESTIONS_PATH")

    redis_client = redis.from_url(redis_url, decode_responses=True)

    questions_answers = {}

    for filename in os.listdir(questions_path):
        with open(os.path.join(questions_path, filename), "r", encoding="koi8-r") as file:
            content = file.read()

    blocks = content.split("\n\n")
    question = None

    for block in blocks:
        if block.startswith("Вопрос"):
            question = block.split(":\n", 1)[1].strip()
        elif block.startswith("Ответ") and question:
            answer = block.split(":\n", 1)[1].strip()
            questions_answers[question] = answer


    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:

            user_id = event.user_id
            user_message = event.text

            if user_message == "Новый вопрос":
                question = random.choice(list(questions_answers.keys()))
                redis_client.set(user_id, question)
                send_message(user_id, question)

            elif user_message == "Сдаться":
                question = redis_client.get(user_id)

                if not question:
                    send_message(user_id, "Сначала нажмите «Новый вопрос».")
                    continue

                answer = questions_answers[question]
                send_message(user_id, f"Правильный ответ: {answer}")

                new_question = random.choice(list(questions_answers.keys()))
                redis_client.set(user_id, new_question)
                send_message(user_id, new_question)

            else:
                question = redis_client.get(user_id)

                if not question:
                    send_message(user_id, "Нажмите «Новый вопрос».")
                    continue

                correct_answer = questions_answers[question]
                correct_answer = clean_answer(correct_answer)

                if user_message.lower() in correct_answer:
                    send_message(
                        user_id,
                        "Правильно! Поздравляю! Нажмите «Новый вопрос».",
                    )
                else:
                    send_message(user_id, "Неправильно… Попробуешь ещё раз?")


if __name__ == "__main__":
    main()
