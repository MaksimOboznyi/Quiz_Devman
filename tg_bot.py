import os
import random
from enum import Enum

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from quiz_questions import load_questions_from_directory, clean_answer


redis_client = None
questions_answers = {}


class BotStates(Enum):
    QUIZ = 1


def start(update, context):
    keyboard = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счёт"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        "Привет! Я бот для викторин!",
        reply_markup=reply_markup,
    )


def handle_new_question_request(update, context):
    chat_id = update.message.chat_id
    user_key = f"tg-{chat_id}"
    question = random.choice(list(questions_answers.keys()))

    redis_client.set(user_key, question)
    update.message.reply_text(question)

    return BotStates.QUIZ


def handle_solution_attempt(update, context):
    chat_id = update.message.chat_id
    user_key = f"tg-{chat_id}"
    user_answer = update.message.text.strip().lower()

    question = redis_client.get(user_key)

    if not question:
        update.message.reply_text("Сначала нажмите «Новый вопрос».")
        return ConversationHandler.END

    correct_answer = questions_answers[question]
    cleaned_correct_answer = clean_answer(correct_answer)

    if user_answer in cleaned_correct_answer:
        update.message.reply_text(
            "Правильно! Поздравляю! Для следующего вопроса нажмите «Новый вопрос»."
        )
        return ConversationHandler.END

    update.message.reply_text("Неправильно… Попробуешь ещё раз?")
    return BotStates.QUIZ


def handle_give_up(update, context):
    chat_id = update.message.chat_id
    user_key = f"tg-{chat_id}"
    question = redis_client.get(user_key)

    if not question:
        update.message.reply_text("Сначала нажмите «Новый вопрос».")
        return ConversationHandler.END

    correct_answer = questions_answers[question]
    update.message.reply_text(f"Правильный ответ: {correct_answer}")

    new_question = random.choice(list(questions_answers.keys()))
    redis_client.set(user_key, new_question)
    update.message.reply_text(new_question)

    return BotStates.QUIZ


def handle_score(update, context):
    update.message.reply_text("Счёт пока не реализован.")
    return BotStates.QUIZ


def main():
    global redis_client, questions_answers

    load_dotenv()

    tg_token = os.environ["TG_BOT_TOKEN"]
    redis_url = os.environ["REDIS_URL"]
    questions_path = os.environ["QUESTIONS_PATH"]

    redis_client = redis.from_url(
        redis_url,
        decode_responses=True,
    )
    questions_answers = load_questions_from_directory(questions_path)

    updater = Updater(tg_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(Filters.regex("^Новый вопрос$"), handle_new_question_request),
        ],
        states={
            BotStates.QUIZ: [
                MessageHandler(Filters.regex("^Новый вопрос$"), handle_new_question_request),
                MessageHandler(Filters.regex("^Сдаться$"), handle_give_up),
                MessageHandler(Filters.regex("^Мой счёт$"), handle_score),
                MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
        ],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
