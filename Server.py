import asyncio
import aiohttp
from urllib.parse import urlencode


class TaskManager:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.auth_hash = None
        self.token = None
        self.u_hash = None

    async def fetch(self, session, url, method="GET", data=None):
        async with session.request(method, url, data=data) as response:
            return await response.json()

    async def get_auth_hash(self, session):
        url = "https://ibronevik.ru/taxi/c/tutor/api/v1/auth"
        data = {'login': self.login, 'password': self.password, 'type': 'e-mail'}
        response_json = await self.fetch(session, url, method="POST", data=data)

        if response_json.get('status') != 'success':
            raise Exception(f"Auth Error: {response_json.get('message', 'auth response error')}")

        self.auth_hash = response_json.get('auth_hash')
        return self.auth_hash

    async def get_token(self, session):
        if not self.auth_hash:
            await self.get_auth_hash(session)

        url = "https://ibronevik.ru/taxi/c/tutor/api/v1/token"
        data = {'auth_hash': self.auth_hash}
        response_json = await self.fetch(session, url, method="POST", data=data)

        if response_json.get('status') != 'success':
            raise Exception(f"Token Error: {response_json.get('message', 'token response error')}")

        self.token = response_json['data']['token']
        self.u_hash = response_json['data']['u_hash']
        return {'token': self.token, 'u_hash': self.u_hash}

    async def get_task(self, session, tl_id='1'):
        data = {'token': self.token, 'u_hash': self.u_hash, 'tl_id': tl_id}
        url = f'https://ibronevik.ru/taxi/c/tutor/api/v1/data/'
        encoded_data = urlencode(data)
        response_json = await self.fetch(session, url, method="POST", data=encoded_data)

        if response_json.get('status') != 'success':
            raise Exception(f"Task Error: {response_json.get('message', 'task response error')}")

        task_list = response_json.get('data').get("data").get("task_action_functions").items()
        return task_list

    async def get_all_tasks(self, session):
        data = {'token': self.token, 'u_hash': self.u_hash}
        url = f'https://ibronevik.ru/taxi/c/tutor/api/v1/data/task_action'
        encoded_data = urlencode(data)
        response_json = await self.fetch(session, url, method="POST", data=encoded_data)

        if response_json.get('status') != 'success':
            raise Exception(f"All Tasks Error: {response_json.get('message', 'all tasks response error')}")

        all_tasks = response_json.get('data').get('data').get("task_actions", {}).items()
        return all_tasks

    async def check_tasks(self):
        async with aiohttp.ClientSession() as session:
            # Инициализируем все необходимые данные при запуске
            await self.get_token(session)

            while True:
                # Каждые 5 секунд проверяем список задач
                task_list = await self.get_task(session)
                all_tasks = await self.get_all_tasks(session)

                # Проходим по каждой задаче и возвращаем её через генератор
                for (task_id, task_data) in task_list:
                    yield task_id, task_data

                await asyncio.sleep(5)  # Задержка 5 секунд между запросами

    async def start_monitoring(self):
        async for task in self.check_tasks():
            yield task
