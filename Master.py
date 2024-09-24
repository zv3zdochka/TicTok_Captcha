import asyncio
import uuid
import json
from Captcha import Bot
from Bot import call_operator
import pickle
from Server import TaskManager


# noinspection PyAsyncCall


class Master:
    def __init__(self):
        self.bots = {}

        self.strim = []
        self.ready = []
        self.working = []

        self.anydesk_id = 1960037423
        self.anydesk_pass = "helloboba12"

    async def change_status(self):
        pass

    async def new_bot(self):
        id = uuid.uuid4()

        credentials = self.get_new_data()

        data = {"url": "https://tiktok.com",
                "id": str(id),
                "proxy_cr": "85.209.197.28:30041",
                "login": credentials[0],
                "password": credentials[1],
                "timeout": 60,
                "delay": 5,
                'proxy_password': "f2e7fc665b",
                'proxy_login': "1e29f06e"
                }

        with open(fr"bots\{str(id)}.json", 'w') as f:
            json.dump(data, f)

        try:
            cookies = pickle.load(open(fr"bots\{str(id)}.pkl", "rb"))
        except FileNotFoundError:
            cookies = None

        bot = Bot(id, cookies)

        asyncio.create_task(bot.run())
        self.bots[id] = bot

        return

    @staticmethod
    def get_new_data():
        # return 'buba2360', 'Oleg.2006.123'
        # return 'guger1231', 'Oleg.2006.'
        return 'captchatester123', 'HelloWorld123!'
        # return "", "Hello.World.123"

    @staticmethod
    def get_strim_link():
        return "https://vt.tiktok.com/ZSYT6ekr9/"

    @staticmethod
    async def rule():
        while True:
            await asyncio.sleep(1)

    async def login_to_tt(self, args: dict):
        for id, bot in self.bots.items():
            if bot.bot_status == 1 and id not in self.working:  # bot is created and ready to work
                await bot.add_task(args)
                print("Send to login")
                return

    async def like_on_strim(self, args):
        # некий функционал по отбору для лайка
        for id, bot in self.bots.items():
            await bot.add_task(args)
            print("send like")
            return

    async def comment_on_strim(self, args):
        # некий функционал по отбору для comment
        for id, bot in self.bots.items():
            await bot.add_task(args)
            print("send comment")
            return

    async def to_strim(self, args):
        for id, bot in self.bots.items():
            await bot.add_task(args)
            print('send to strim')
            self.strim.append(id)
            return
        await asyncio.sleep(5)

    async def exit_strim(self, args):
        for id, bot in self.bots.items():
            if bot.bot_status == 0 and id not in self.working and id not in self.strim and id in self.ready:
                asyncio.create_task(bot.enter_strim())
                self.strim.append(id)
                return
        await asyncio.sleep(5)

    async def exit_tik_tok(self, args):
        for id, bot in self.bots.items():
            await bot.add_task(args)
            return

    async def call_oper(self):
        await call_operator(
            f"Connect with Anydesk, using this id {self.anydesk_id} and this password {self.anydesk_pass}")


class Power(Master):
    def __init__(self):
        super().__init__()

    async def main(self):
        m = Master()
        s = TaskManager(login='bot@ibronevik.ru', password='btw0rd')

        # Асинхронно обрабатываем задачи от TaskManager
        async def process_tasks():
            async for task_id, task_data in s.start_monitoring():
                if int(task_id) == 6:
                    task_list = sorted(list(task_data.get('row')), key=lambda x: int(x.get('index')))
                    for i in task_list:
                        print(i)
                        func_id = int(i.get('task_action'))
                        match func_id:
                            case 8:
                                # create new bot
                                await self.new_bot()


                            case 9:
                                # login it to tt
                                await self.login_to_tt({"task_num": 9, "args": i})

                            case 15:
                                # push into strim
                                await self.to_strim({"task_num": 15, "args": i})

                            case 5:
                                'wait'
                                pass

                            case 3:
                                # like on strim
                                await self.like_on_strim({"task_num": 3, "args": i})
                                pass

                            case 11:
                                # exit tt
                                await self.exit_tik_tok({"task_num": 11, "args": i})
                                break

                    print('task sent')
                    await asyncio.sleep(10000)

        await asyncio.gather(
            m.rule(),
            process_tasks()
        )


if __name__ == "__main__":
    P = Power()
    asyncio.run(P.main())
