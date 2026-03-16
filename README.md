# Quiz Bot

Telegram и VK боты для викторины.

Бот задаёт пользователю случайный вопрос и проверяет правильность ответа.  
Если ответ правильный — бот поздравляет пользователя.  
Если неправильный — предлагает попробовать ещё раз.

Бот использует Redis для хранения текущего вопроса пользователя.

---

## Telegram Bot

Telegram бот доступен по ссылке:

https://t.me/YOUR_TELEGRAM_BOT

---

## VK Bot

VK бот доступен по ссылке:

https://vk.com/YOUR_GROUP

---

## Как запустить локально

1. Клонировать репозиторий

'''bash
git clone https://github.com/MaksimObozniy/Quiz_Devman.git

cd Quiz_Devman
'''

2. Создать виртуальное окружение

'''bash
python3.9 -m venv venv
source venv/bin/activate
'''

3. Установить зависимости

'''bash
pip install -r requirements.txt
'''

4. Создать файл '.env'

TG_BOT_TOKEN=your_token
VK_TOKEN=your_vk_token
REDIS_URL=your_redis_url
QUESTIONS_PATH=question_path


5. Запустить бота

Telegram бот:

python tg_bot.py

----------------------------

VK бот:

python vk_bot.py
