import os, logging, requests, time

import telegram
from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/{method}/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    is_keys_invalid = homework_name is None or homework_status is None
    is_status_invalid = homework_status not in ['rejected', 'approved']
    
    if is_keys_invalid or is_status_invalid:
        error_message = 'Неверный ответ сервера'
        logging.error(error_message)
        return error_message

    homework_name = homework.get('homework_name')

    if homework.get('status')  == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif homework.get('status') == 'approved':
        verdict = (
            f'Ревьюеру всё понравилось, можно приступать '
            f'к следующему уроку.'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            API_URL.format(method='homework_statuses'),
            headers=headers,
            params=params
        )
        return homework_statuses.json()
    except (requests.exceptions.RequestException) as e:
        logging.error(f'Произошла ошибка {e}')
        return {}



def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
