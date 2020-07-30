import os
import logging
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN") # Определение констант вне кода
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') # Константы капсами в .env и в коде
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/{method}/' # Замечания из предыдущего проекта


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    try:
        if homework['status']  == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif homework['status'] == 'approved':
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        else:
            verdict = 'Статусы API неожиданно изменились, проверьте документацию API '
    except KeyError as e:
        logging.error(f'Произошла ошибка {e}')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp or None}
    try:
        homework_statuses = requests.get(
            API_URL.format(method='homework_statuses'),
            headers=headers,
            params=params
        )
        return homework_statuses.json()
    except (requests.exceptions.RequestException) as e:
        logging.error(f'Произошла ошибка {e}')
        return str(e)



def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp 29 июля 2020 = 1596058073

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
