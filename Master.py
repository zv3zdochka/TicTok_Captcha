import asyncio
import uuid
import json
from Captcha import Bot
from Bot import call_operator
import pickle
from Server import TaskManager

class Master:
    def __init__(self):
        self.bots = {}

        self.processing = []
        self.online = []
        self.on_strim = []

        self.anydesk_id = 1960037423
        self.anydesk_pass = "helloboba12"

    async def new_bot(self):
        id = uuid.uuid4()

        credentials = self.get_new_data()

        data = {"url": "https://tiktok.com",
                "id": str(id),
                "proxy_cr": "83.171.234.72:30041",
                "login": credentials[0],
                "password": credentials[1],
                "timeout": 60,
                "delay": 5,
                'proxy_password': "96f869afe5",
                'proxy_login': "f9c66f96"
                }


        with open(fr"bots\{str(id)}.json", 'w') as f:
            json.dump(data, f)

        try:
            cookies = pickle.load(open(fr"bots\{str(id)}.pkl", "rb"))
        except FileNotFoundError:
            cookies = None

        bot = Bot(id, cookies)
        self.bots[id] = bot

        return


    @staticmethod
    def get_new_data():
        return 'guger1231', 'Oleg.2006.'
        #return 'captchatester123', 'HelloWorld123!'
        #return "", "Hello.World.123"


    @staticmethod
    def get_strim_link():
        return "https://vt.tiktok.com/ZSYT6ekr9/"


    @staticmethod
    async def rule():
        while True:
            print('Search')
            await asyncio.sleep(1)

    async def login_to_tt(self):
        for id, bot in self.bots.items():
            if bot.bot_status == 1 and id not in self.processing:  # bot is created and ready to work

                # noinspection PyAsyncCall
                await asyncio.create_task(bot.start_bot())

                self.processing.append(id)
                await asyncio.sleep(60)
                print(f"Task for bot {id} has been started.")
                self.processing.remove(id)
                self.online.append(id)
                return

    async def to_strim(self):
        for id, bot in self.bots.items():
            if bot.bot_status == 0 and id not in self.processing and id not in self.on_strim and id in self.online:
                await asyncio.create_task(bot.enter_strim())
                self.on_strim.append(id)
                return

    async def call_oper(self):
        await call_operator(
            f"Connect with Anydesk, using this id {self.anydesk_id} and this password {self.anydesk_pass}")


class Server(Master):
    def __init__(self):
        super().__init__()

    async def find_task(self):
        task = 1
        while True:
            print(f"Task {task}")
            match task:
                case 1:  # create new bot
                    await self.new_bot()
                    print('Bot created')
                    task += 1

                case 2:  # login bot to tt
                    await self.login_to_tt()
                    print('Bot login')
                    task += 1

                case 3:  # send bot to strim
                    await self.to_strim()
                    print('Enter Strim')

            await asyncio.sleep(1)


# async def main():
#
#     m = Master()
#     s = Server()
#
#     await asyncio.gather(
#         m.rule(),
#         s.find_task()
#     )


async def main():
    m = Master()
    s = TaskManager(login='bot@ibronevik.ru', password='btw0rd')

    # Асинхронно обрабатываем задачи от TaskManager
    async def process_tasks():
        async for task_id, task_data in s.start_monitoring():
            print(f"Получена задача: {task_id} с данными: {task_data}")
            # Здесь можно обработать каждую задачу, например вызвать метод у m

    await asyncio.gather(
        m.rule(),
        process_tasks()
    )


if __name__ == "__main__":
    asyncio.run(main())

