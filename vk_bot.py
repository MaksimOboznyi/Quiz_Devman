import os
import random
from functools import partial

import redis
import vk_api
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from quiz_questions import load_questions_from_directory, clean_answer


def get_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Мой счёт", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def send_message(vk, user_id, text):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=0,
        keyboard=get_keyboard(),
    )


def handle_new_question_request(vk, redis_client, questions_answers, user_id):
    user_key = f"vk-{user_id}"

    question = random.choice(list(questions_answers.keys()))
    redis_client.set(user_key, question)
    send_message(vk, user_id, question)


def handle_give_up(vk, redis_client, questions_answers, user_id):
    user_key = f"vk-{user_id}"
    question = redis_client.get(user_key)

    if not question:
        send_message(vk, user_id, "Сначала нажмите «Новый вопрос».")
        return

    answer = questions_answers[question]
    send_message(vk, user_id, f"Правильный ответ: {answer}")

    new_question = random.choice(list(questions_answers.keys()))
    redis_client.set(user_key, new_question)
    send_message(vk, user_id, new_question)


def handle_score(vk, user_id):
    send_message(vk, user_id, "Счёт пока не реализован.")


def handle_solution_attempt(vk, redis_client, questions_answers, user_id, user_message):
    user_key = f"vk-{user_id}"
    question = redis_client.get(user_key)

    if not question:
        send_message(vk, user_id, "Нажмите «Новый вопрос».")
        return

    correct_answer = questions_answers[question]
    cleaned_answer = clean_answer(correct_answer)

    if user_message.lower() in cleaned_answer:
        send_message(
            vk,
            user_id,
            "Правильно! Поздравляю! Нажмите «Новый вопрос».",
        )
        return

    send_message(vk, user_id, "Неправильно… Попробуешь ещё раз?")


def main():
    load_dotenv()

    vk_token = os.environ["VK_BOT_TOKEN"]
    redis_url = os.environ["REDIS_URL"]
    questions_path = os.environ["QUESTIONS_PATH"]

    redis_client = redis.from_url(redis_url, decode_responses=True)
    questions_answers = load_questions_from_directory(questions_path)

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    new_question_handler = partial(
        handle_new_question_request,
        vk,
        redis_client,
        questions_answers,
    )
    give_up_handler = partial(
        handle_give_up,
        vk,
        redis_client,
        questions_answers,
    )
    score_handler = partial(handle_score, vk)
    solution_attempt_handler = partial(
        handle_solution_attempt,
        vk,
        redis_client,
        questions_answers,
    )

    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue

        user_id = event.user_id
        user_message = event.text

        if user_message == "Новый вопрос":
            new_question_handler(user_id)
            continue

        if user_message == "Сдаться":
            give_up_handler(user_id)
            continue

        if user_message == "Мой счёт":
            score_handler(user_id)
            continue

        solution_attempt_handler(user_id, user_message)


if __name__ == "__main__":
    main()