import re
from datetime import datetime
from bot import Bot


def add_task(bot: Bot, message: str) -> bool:
    """
    Добавление новой задачи

    :param bot: объект бота
    :param message: сообщение пользователя
    :return: удалось ли добавить задачу
    """

    try:
        priority = int(message[0])
        message = message.replace(str(priority), '')
    except ValueError:
        priority = None

    try:
        tags_list = re.findall(r'\((.+)\)', message)[0]
        message = message.replace(f'({tags_list})', '')
        tags_list = tags_list.split(', ')
    except IndexError:
        tags_list = None

    try:
        date = re.findall(r'\[(.+)\]', message)[0]
        message = message.replace(f'[{date}]', '')
    except IndexError:
        date = None

    title: str = re.findall(r'.+', message)[0].strip()

    start = end = None
    if date:
        if '-' in date:
            start, end = date.split(' - ')
            try:
                start = datetime.strptime(start, '%d.%m %H:%M').replace(datetime.now().year).isoformat()
                end = datetime.strptime(end, '%d.%m %H:%M').replace(datetime.now().year).isoformat()
            except ValueError:
                start = datetime.strptime(start, '%d.%m').replace(datetime.now().year).isoformat()[:10]
                end = datetime.strptime(end, '%d.%m').replace(datetime.now().year).isoformat()[:10]
        elif 'завтра в ' in date:
            h, m = map(int, re.findall(r'\d\d:\d\d', message)[0].split(':'))
            today = datetime.now().day
            start = datetime.now().replace(day=today + 1, hour=h, minute=m).isoformat()
        elif 'завтра' in date:
            today = datetime.now().day
            start = datetime.now().replace(day=today + 1).isoformat()[:10]
        elif 'сегодня в ' in date:
            h, m = map(int, re.findall(r'\d\d:\d\d', message)[0].split(':'))
            start = datetime.now().replace(hour=h, minute=m).isoformat()
        elif 'сегодня' in date:
            start = datetime.now().replace().isoformat()[:10]
        else:
            try:
                start = datetime.strptime(date, '%d.%m %H:%M').replace(datetime.now().year).isoformat()
            except ValueError:
                start = datetime.strptime(date, '%d.%m').replace(datetime.now().year).isoformat()[:10]

    if end:
        date = {"start": start, "end": end}
    elif date:
        date = {"start": start}


    parent = {"type": "database_id", "database_id": bot.db_id}
    properties = {}
    properties.update({'Name': {"title": [{"text": {"content": title}}]}})
    properties.update({'Checked': {"checkbox": False}})
    if date:
        properties.update({'Date': {"date": date}})
    if priority:
        properties.update({'Priority': {"select": {"name": str(priority)}}})
    if tags_list:
        tags = []
        for tag in tags_list:
            tags.append({"name": tag})
        properties.update({'Tags': {"multi_select": tags}})

    bot.notion.pages.create(parent=parent, properties=properties)
    return True