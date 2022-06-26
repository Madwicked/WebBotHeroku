import telebot
from telebot import types
import json
import os

token = os.environ['TELEGRAM_TOKEN']


bot = telebot.TeleBot(token)
MAIN_STATE = 'main'
CITY_STATE = 'city'
WEATHER_DATE_STATE = 'weather_date_handler'  # почему-то у него weather_date_handler
#states = {}


try: #ловит исключения, типа если нет файла, то создает
    data = json.load(open('data.json', 'r', encoding='utf-8'))
except FileNotFoundError:
    data = {
        'states': {},
        MAIN_STATE: {

        },
        CITY_STATE: {

        },
        WEATHER_DATE_STATE: {
            # id:city
        },
    }
def change_data(key, user_id, value):
    data[key][user_id]=value
    json.dump(
        data,
        open('data.json', 'w', encoding='utf-8'),
        indent=4,
        ensure_ascii=False,  # сохраняет русские символы
    )



@bot.message_handler(func=lambda message: True)
def dispecher(message):
    #    print(states)
    user_id = str(message.from_user.id)

    state = data['states'].get(user_id, MAIN_STATE)

    if state == MAIN_STATE:
        main_handler(message)
    elif state == CITY_STATE:
        city_handler(message)
    elif state == WEATHER_DATE_STATE:
        weather_date(message)


def main_handler(message):
    user_id = str(message.from_user.id)
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Погода'))

        bot.send_message(
            user_id,
            'Это бот погоды',
            reply_markup=markup,
        )
        change_data('states', user_id, MAIN_STATE)
    # print(message)
    elif message.text.lower() == 'погода':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(
            *[types.KeyboardButton(button) for button in ['мск', 'спб']]
        )
        bot.send_message(user_id, 'Город? мск или спб', reply_markup=markup)

        change_data('states',user_id, CITY_STATE)



    else:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, 'моя твоя не понимать', reply_markup=markup)


def city_handler(message):
    user_id = str(message.from_user.id)
    if message.text.lower() in ['мск', 'спб']:
        change_data(WEATHER_DATE_STATE, user_id,message.text.lower())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(
            *[types.KeyboardButton(button) for button in ['сегодня', 'завтра']]
        )
        bot.send_message(user_id, 'Када? Введи "сегодня" или "завтра"', reply_markup=markup)
        change_data('states', user_id, WEATHER_DATE_STATE)
    else:
        bot.reply_to(message, 'моя твоя не понимать')


WEATHER = {
    'спб': {
        'сегодня': 27,
        'завтра': 32,

    },
    'мск': {
        'сегодня': -5,
        'завтра': -15,
    }
}


def weather_date(message):
    user_id = str(message.from_user.id)
    city = data[WEATHER_DATE_STATE][user_id]

    if message.text == 'сегодня':
        bot.send_message(user_id, WEATHER[city][message.text.lower()])
        change_data('states',user_id, MAIN_STATE)

    elif message.text == 'завтра':
        bot.send_message(user_id, WEATHER[city][message.text.lower()])
        change_data('states', user_id, MAIN_STATE)
    elif message.text.lower() == 'назад':
        bot.send_message(user_id, 'Вернулся назад')
        change_data('states', user_id, MAIN_STATE)
    else:
        bot.reply_to(message, 'моя твоя не понимать')


if __name__ == '__main__':
    bot.polling()
    print('бот остановлен')