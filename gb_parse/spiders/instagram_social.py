import scrapy
import json
from collections import defaultdict, deque
from anytree import Node, RenderTree
from scrapy.exceptions import CloseSpider


class InstagramSocialSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]

    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _graphql_url = "/graphql/query/"

    # Словарь хэшей для получения url'ов following и followed_by
    _query_hashes_map = {
        "edge_followed_by": "c76146de99bb02f6415203be841dd25a",
        "edge_follow": "d04b0a864b4b54837c0d870b0e77e076",
    }

    _follow_dict = defaultdict(lambda: defaultdict(list))
    _tree_dict = {}

    def __init__(self, login, password, users, log_level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем пользоваиелей, между которыми нужно найти связь
        self._first_user = users[0]
        self._second_user = users[1]
        # Создаем дерево и в его корень определяем стартового юзера
        self._tree_dict[self._first_user] = Node(self._first_user)
        # Очередь url'ов, для запросов в порядке удаления от стартового юзера
        self.scan_que = deque()
        # Логин и пароль для авторизации паука
        self.login = login
        self.password = password
        # Уровень логгирования
        self.log_level = log_level

    @staticmethod
    def get_data_from_script(response) -> dict:
        """
        Функция для парсинга json
        :param response: Принимаем response для парсинга json'a
        :return: Возвращает json объект в виде словаря
        """
        try:
            return json.loads(
                response.xpath('//script[contains(text(),"window._sharedData")]/text()')
                .get()
                .replace("window._sharedData = ", "")
                .rstrip(";")
            )
        except ValueError:
            raise CloseSpider("Проблема с JSON форматом")

    def _get_url(self, user_id, after="", flw="edge_followed_by") -> str:
        """
        Функция для формирования пути(при скролле пользователей) для запросов
        :param user_id: id пользователя инстраграм
        :param after: значение end_cursor'a. Хэш, необходим инстаграму для того чтобы знать, с какого места загружать пользователей.
        :param flw: Хэш following или followed_by
        :return: Возвращает url для запроса
        """
        variables = {
            "id": user_id,
            "include_reel": False,
            "fetch_mutual": False,
            "first": 100,
            "after": after,
        }
        return f"{self._graphql_url}?query_hash={self._query_hashes_map[flw]}&variables={json.dumps(variables)}"

    def parse(self, response, **kwargs):
        # авторизуемся
        try:
            data = self.get_data_from_script(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": data["config"]["csrf_token"]},
            )
        except AttributeError:
            # Если получили ошибку, то есть шанс, что авторизовались
            data = response.json()
            if data["authenticated"]:
                yield response.follow(f"/{self._first_user}/", callback=self._user_parse)

    def _user_parse(self, response):
        """
        Функция из response'a получает json структуру из скрипта, содержащего нужные нам данные.
        Кроме того, в response.meta передаем данные о пользователе, чей json мы парсим
        :param response: Принимаем response для парсинга json'a
        :return: Посылаем json структуру на дальнейшую обработку
        """
        json_data = self.get_data_from_script(response)
        try:
            json_user = json_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
            user_id = json_user["id"]
            user_name = json_user["username"]
            followed_by_count = json_user["edge_followed_by"]["count"]
            follow_count = json_user["edge_follow"]["count"]

            # Проходим по хэшам. В мета данные передаем данные, которые потом используем при парсинге  подписчиков и на кого пользователь подписался
            for flw in self._query_hashes_map.keys():
                yield response.follow(
                    self._get_url(user_id, flw=flw),
                    callback=self._follow_parse,
                    meta={
                        "user_id": user_id,
                        "user_name": user_name,
                        "follow": flw,
                        "followed_by_count": followed_by_count,
                        "follow_count": follow_count,
                        "parent": response.meta.get("parent"),
                    },
                )
        except KeyError:
            raise CloseSpider("Wrong JSON received. Probably bad user for crawling...")

    def _follow_parse(self, response):
        """
        Функция принимает response в виде json структуры, парсит всех подписчиков и на кого пользователь подписался [following и followed_by],
        берет пересечение этих множеств. По результирующему множеству делаем обход в порядке FIFO с целью
        нахождения последнего пользователя в цепочке. Если нашли пагинацию - идем по ней, через yield на саму себя
        :param response: принимаем response в форме json.
        """
        json_data = response.json()
        end_cursor = json_data["data"]["user"][response.meta["follow"]]["page_info"]["end_cursor"]
        next_page = json_data["data"]["user"][response.meta["follow"]]["page_info"][
            "has_next_page"
        ]
        user_name = response.meta["user_name"]

        # Подгружаем следующую страницу
        if next_page:
            yield response.follow(
                self._get_url(
                    user_id=response.meta["user_id"], after=end_cursor, flw=response.meta["follow"]
                ),
                callback=self._follow_parse,
                meta=response.meta,
            )

        # Обходим всех пользователей, сортируя их по словарям  всех подписчиков и на кого пользователь подписался [following и followed_by]
        edges = json_data["data"]["user"][response.meta["follow"]]["edges"]
        if self.log_level:
            print(f"EDGES: ${len(edges)}")
        for edge in edges:
            if response.meta["follow"] == "edge_follow":
                self._follow_dict[user_name]["follows"].append(edge["node"]["username"])
            else:
                self._follow_dict[user_name]["followed_by"].append(edge["node"]["username"])

        if self.log_level:
            print(
                f'{user_name}: follows {len(self._follow_dict[user_name]["follows"])} '
                f'| {response.meta["follow_count"]}, '
                f'followed_by {len(self._follow_dict[user_name]["followed_by"])} '
                f'| {response.meta["followed_by_count"]}'
            )

        # При условии, что количество обработаных пользователей following и followed_by равно итоговому - забираем
        # пересечение этих множеств и помещаем их в очередь для дальнейшего обхода.
        if (len(self._follow_dict[user_name]["follows"]) == response.meta["follow_count"]) and (
            len(self._follow_dict[user_name]["followed_by"]) == response.meta["followed_by_count"]
        ):
            full_follow = []  # список пользвателей, которые и following, и followed_by.
            if self.log_level:
                print(f"BY_FOLLOW: ${len(full_follow)}")
            for user in self._follow_dict[user_name]["followed_by"]:
                if user in self._follow_dict[user_name]["follows"]:
                    full_follow.append(user)
                    # создаем дерево, но с условием, что пользователя в дерево еще не помещали
                    if user not in self._tree_dict.keys():
                        self._tree_dict[user] = Node(user, parent=self._tree_dict[user_name])

            if self.log_level:
                print(RenderTree(self._tree_dict[self._first_user]))

            # Помещаем список пользователей в очередь
            self.scan_que.extend(full_follow)

            if self.log_level:
                print(f"\nКоличество пользователей в очереди: {len(self.scan_que)}")

            # Если  мы нашли конечного пользователя - пишем об этом в консоль, рисуем цепочку связей и завершаем работу паука
            if self._second_user in full_follow:
                print(
                    f"\nКоличество переходов между пользователями {self._first_user} и {self._second_user}: "
                    f"{self._tree_dict[self._second_user].depth}"
                )
                print("Путь:")
                print(
                    " -> ".join(
                        [
                            node.name
                            for node in self._tree_dict[self._second_user].iter_path_reverse()
                        ]
                    )
                )
                raise CloseSpider("Связь между пользователями обнаружена. Остановка паука")

        try:
            # Берем из очереди пользователя. Если очередь пуста - мы проверили одну из цепочек пользователей
            # инсты и не нашли связей
            user = self.scan_que.popleft()
            yield response.follow(
                f"/{user}/", callback=self._user_parse, meta={"parent": user_name}
            )
        except IndexError:
            print("Очередь пуста.")
