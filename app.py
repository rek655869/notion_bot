from configparser import ConfigParser
import requests
import schedule

from bot import Bot
import commands


config = ConfigParser()
config.read('config.ini')

notion_session = requests.session()
notion_session.headers.update({'Authorization': f"Bearer {config['DEFAULT']['Notion_token']}",
                               'Notion-Version': "2022-02-22"})
bot = Bot(config['DEFAULT']['TG_token'])
bot.db_id = config['DEFAULT']['DB_ID']
bot.notion = notion_session
chat_id = 944652106


def send_schedule():
    bot.send_message(chat_id, *commands.get_schedule(bot))


schedule.every().day.at("21:10").do(send_schedule)

while True:
    schedule.run_pending()

    event = bot.getUpdates()
    if event is not None:
        if 'message' in event:
            text = event['message']['text']
            message_id = event['message']['message_id']

            if event['message']['chat']['id'] != chat_id:
                continue

            # расписание на день
            if '/day' in text:
                message, keyboard = commands.get_schedule(bot)
                bot.send_message(chat_id, message, keyboard)

            # если команд нет, значит это добавление новой задачи
            else:
                if commands.add_task(bot, text):
                    bot.send_message(chat_id, 'Внесено!')
                else:
                    bot.send_message(chat_id, 'Не понимаю')

        elif 'callback_query' in event:
            # выполнение задачи
            old_message = event['callback_query']['message']
            message, keyboard = commands.complete_task(bot, event['callback_query']['data'], old_message)
            bot.edit_message(old_message['chat']['id'], old_message['message_id'], message, keyboard)
            bot.congratulate(event['callback_query']['id'])

