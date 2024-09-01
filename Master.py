import asyncio
import uuid
import json
from Captcha import Bot
from Bot import call_operator
import pickle

# temp
new_data = 0


class Master:
    def __init__(self):
        self.bots = {}
        self.logining = []
        self.on_strim = []
        self.anydesk_id = 1960037423
        self.anydesk_pass = "helloboba12"

    async def new_bot(self):
        id = uuid.uuid4()
        new_data = self.get_new_data()
        data = {"url": "https://tiktok.com",
                "id": str(id),
                "proxy": "35.185.196.38:3128",
                "login": new_data[0],
                "password": new_data[1],
                "timeout": 60,
                "delay": 5}

        with open(fr"bots\{str(id)}.json", 'w') as f:
            json.dump(data, f)

        cookies = pickle.load(open("cookies.pkl", "rb"))

        bot = Bot(id, cookies)
        self.bots[id] = bot

    def get_new_data(self):
        global new_data
        if new_data == 0:
            new_data = 1
            return 'captchatester123', 'HelloWorld123!'

        else:
            return 'guger1231', 'Oleg.2006.'

    def get_strim_link(self):
        return "https://vt.tiktok.com/ZSYT6ekr9/"

    @staticmethod
    async def rule():
        while True:
            await asyncio.sleep(1)

    async def login_to_tt(self):
        for id, bot in self.bots.items():
            if bot.bot_status == 1 and id not in self.logining:
                # await self.call_oper()
                # await asyncio.sleep(7)
                asyncio.create_task(bot.main())
                self.logining.append(id)
                await asyncio.sleep(10)
                print(f"Task for bot {id} has been started.")
                self.logining.remove(id)
                break

    async def to_strim(self):
        for id, bot in self.bots.items():
            if bot.bot_status == 0 and id not in self.logining and id not in self.on_strim:
                await asyncio.create_task(bot.to_strim(self.get_strim_link()))
                self.on_strim.append(id)
                break

    async def call_oper(self):
        await call_operator(
            f"Connect with Anydesk, using this id {self.anydesk_id} and this password {self.anydesk_pass}")


class Server(Master):
    def __init__(self):
        super().__init__()

    async def find_task(self):
        task = 1
        n = 0
        while True:
            print(task)
            match task:
                case 1:  # create new bot
                    await self.new_bot()
                    print('bot created')
                    task += 1

                case 2:  # login bot to tt
                    await self.login_to_tt()
                    print('logined')
                    task += 1

                case 3: # send bot to strim
                    if n == 30:
                        print('starting strimming')
                        await asyncio.sleep(150)
                        #await self.to_strim()
                    n += 1
                    await asyncio.sleep(2)



async def main():
    M = Master()
    S = Server()
    await asyncio.gather(
        M.rule(),
        S.find_task()
    )


if __name__ == "__main__":
    asyncio.run(main())


