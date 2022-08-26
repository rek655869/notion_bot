from typing import Tuple
import json

from bot import Bot


def complete_task(bot: Bot, page_id: str, old_message: dict) -> Tuple[str, str]:
    """
    Выполнение задачи по нажатию на кнопку. Она отмечается в Notion, а бот редактирует сообщение, убирая пункт из списка

    :param bot: объект бота
    :param page_id: ID страницы в Notion, пришедший в callback_data
    :param old_message: объект старого сообщения бота
    :return: текст и клавиатура для обновлённого сообщения
    """

    # получаем старые кнопки, вытаскиваем нужную и удаляем её из списка
    buttons = old_message['reply_markup']['inline_keyboard']
    buttons = [x for l in buttons for x in l]
    to_drop = list(filter(lambda x: x if x.get('callback_data') == page_id else None, buttons))[0]
    buttons.remove(to_drop)

    # убираем строку из сообщения
    elements = list(old_message['text'].split('\n'))
    for i in range(len(elements)):
        if to_drop.get('text') in elements[i].split('.')[0]:
            elements.pop(i)
            break

    # заново проставляем нумерацию
    # в тексте
    count = 0
    for i in range(len(elements)):
        count += 1
        other = elements[i].split('.')[1:]
        elements[i] = f'`{count}.`{".".join(other)}'
    # в кнопках
    count = 0
    for i in range(len(buttons)):
        count += 1
        buttons[i].update({'text': count})

    prop = {'Checked': {'checkbox': True}}
    bot.update_page(page_id, properties=prop)

    split_keyboard = [buttons[i:i + 5] for i in range(0, len(buttons), 5)]
    text = '\n'.join(elements).replace('(', '(_').replace(')', '_)').replace('[', '\[')
    return text, json.dumps({'inline_keyboard': split_keyboard})
