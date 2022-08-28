import requests
import json
import random
from typing import Optional, List
from requests import Session

from gratters import gratters


class Bot:

    def __init__(self, token):
        self.url = f'https://api.telegram.org/bot{token}/'
        self.last_update = 0
        self.db_id = None
        self.notion: Session = None

    # ---------- TELEGRAM ---------

    def getUpdates(self) -> Optional[dict]:
        """
        Ака-longpool соединение с Телеграм

        :return объект события или ничего
        """
        data = requests.get(self.url + 'getUpdates', params={'limit': 1, 'offset': self.last_update + 1}).text
        data = json.loads(data)['result']
        if not data:
            return
        else:
            data = data[0]
        if data['update_id'] > self.last_update:
            self.last_update = data['update_id']
        elif data['update_id'] == self.last_update:
            return
        return data

    def send_message(self, chat_id: int, message: str, keyboard: str = None):
        """
        Отправка сообщения пользователю

        :param chat_id: ID пользователя или чата
        :param message: сообщение
        :param keyboard: клавиатура
        """
        requests.post(self.url + 'sendMessage',
                      params={'chat_id': chat_id, 'text': message, 'reply_markup': keyboard,
                              'parse_mode': 'Markdown'})

    def delete_message(self, chat_id: int, message_id: int):
        """
        Удаление сообщения

        :param chat_id: ID пользователя или чата
        :param message_id: ID сообщения, которое нужно удалить
        """
        requests.post(self.url + 'deleteMessage',
                      params={'chat_id': chat_id, 'message_id': message_id})

    def edit_message(self, chat_id: int, message_id: int, message: str, keyboard: str):
        """
        Редактирование сообщения

        :param chat_id: ID пользователя или чата
        :param message_id: ID сообщения, которое нужно отредактировать
        :param message: текст сообщения
        :param keyboard: клавиатура
        """
        requests.post(self.url + 'editMessageText',
                      params={'chat_id': chat_id, 'message_id': message_id, 'text': message,
                              'reply_markup': keyboard, 'parse_mode': 'Markdown'})

    def congratulate(self, callback_id: int):
        """
        Поздравление с выполнением задачи

        :param callback_id: ID события
        """
        requests.post(self.url + 'answerCallbackQuery',
                      params={'callback_query_id': callback_id,
                              'text': gratters[random.randint(0, len(gratters) - 1)]})

    # ---------- NOTION ----------

    def get_pages(self, filter: dict = None, sorts: list = None,
                  start_cursor: str = None, page_size: int = 100) -> List[dict]:
        """
        Получить страницы из базы данных в Notion

        :param filter: условие фильтрации возвращаемых страниц
        :param sorts: упорядочивает результаты на основе предоставленных критериев сортировки
        :param start_cursor: при указании возвращает страницу результатов, начиная с указанного курсора
        :param page_size: кол-во требуемых страниц
        :return: список со страницами
        """
        url = f"https://api.notion.com/v1/databases/{self.db_id}/query"
        payload = {}
        if filter:
            payload.update({'filter': filter})
        if sorts:
            payload.update({'sorts': sorts})
        if start_cursor:
            payload.update({'start_cursor': start_cursor})
        payload.update({'page_size': page_size})
        return self.notion.post(url, json=payload).json()['results']

    def update_page(self, page_id: str, properties: dict):
        """
        Обновление страницы в Notion

        :param page_id: ID страницы
        :param properties: значения свойств этой страницы
        """
        url = "https://api.notion.com/v1/pages/" + page_id
        payload = {"properties": properties}
        self.notion.patch(url, json=payload)

    def create_page(self, properties: dict):
        """
        Создание страницы в Notion

        :param properties: значения свойств этой страницы
        """
        url = "https://api.notion.com/v1/pages"
        payload = {
            'parent': {"type": "database_id", "database_id": self.db_id},
            'properties': properties
        }
        self.notion.post(url, json=payload)
