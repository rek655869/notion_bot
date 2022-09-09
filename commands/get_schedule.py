from datetime import datetime
import json
from typing import Tuple

from bot import Bot
from objects import Page


def get_schedule(bot: Bot) -> Tuple[str, str]:
    """
    Составление сообщения с расписанием на день

    :param bot: объект бота
    :return: текст сообщения и клавиатура
    """
    filter = {
        "and": [
            {
                "property": "Checked",
                "checkbox": {
                    "equals": False
                }
            },
            {
                "property": "Date",
                "date": {
                    "on_or_before": datetime.now().isoformat()
                }
            }
        ]
    }

    sorts = [
        {
            "property": "Priority",
            "direction": "ascending"
        },
        {
            "property": "Tags",
            "direction": "ascending"
        }
    ]

    orig_pages = bot.get_pages(filter=filter, sorts=sorts)
    keyboard = []
    message = ''
    count = 0  # счётчик количества страниц (столько будет пунктов = кнопок)

    for data in orig_pages:
        page = Page(data)

        start = modify_time(page.properties.date['start'])
        end = modify_time(page.properties.date['end']) if page.properties.date['end'] else None

        count += 1
        message += f'`{count}.` {page.properties.priority} {page.properties.title} '
        if page.properties.tags:
            message += f'(_{", ".join(page.properties.tags)}_) '

        if start and end:
            message += f'\[{start} - {end}]\n'
        elif start and not end:
            message += f'\[{start}]\n'
        elif end and not start:
            message += f'\[до {end}]\n'

        keyboard.append({"text": f"{count}", "callback_data": f'{page.id}'})

    split_keyboard = [keyboard[i:i + 5] for i in range(0, len(keyboard), 5)]
    if not message:
        return 'Все задачи выполнены', None
    return message, json.dumps({"inline_keyboard": split_keyboard})



def modify_time(date: str) -> str:
    """
    Перевод даты (со временем) из [Y-m-dTH:M] в [d.m H:M]

    :param date: исходная дата в формате iso
    :return: нормальная, изменённая дата
    """
    date = date if len(date) <= 16 else date[:16]  # убираем секунды и прочий мусор, если есть
    try:
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M').strftime('%d.%m %H:%M')
    except ValueError:
        date = datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m')
    return date
