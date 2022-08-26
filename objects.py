

class Page:

    def __init__(self, data: dict):
        """
        Подробнее [https://developers.notion.com/reference/page]

        :param data: объект, возвращаемый Notion API
        """
        self.id: str = data['id']
        self.properties = Properties(data['properties'])


class Properties:

    def __init__(self, data: dict):
        """
        Подробнее [https://developers.notion.com/reference/property-value-object]

        :param data: объект, возвращаемый Notion API
        """
        self.date: dict = data['Date']['date']  # опционально имеет start и end
        self.tags: list = [tag['name'] for tag in data['Tags']['multi_select']] if data['Tags']['multi_select'] else None
        self.title: str = data['Name']['title'][0]['text']['content']

        self.__priority = data['Priority']['select']


    @property
    def priority(self) -> str:
        """
        Возвращает эмодзи в зависимости от установленного приоритета

        :return: эмодзи или пустая строка
        """
        if self.__priority is None:
            return ''

        if self.__priority['name'] == '1':
            return '🔴'
        elif self.__priority['name'] == '2':
            return '🟠'
        else:
            return '🔵'

