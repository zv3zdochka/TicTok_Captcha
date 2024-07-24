import asyncio
import uuid
import json
from Captcha import Bot


class Master:
    def __init__(self):
        self.bots = {}
        self.online = {}
        self.processing = {}

    async def new_bot(self):
        id = uuid.uuid4()

        data = {"url": "https://tiktok.com",
                "id": str(id),
                "proxy": "35.185.196.38:3128",
                "login": "captchatester123",
                "password": "HelloWorld123!",
                "timeout": 60,
                "delay": 5}

        with open(fr"bots\{str(id)}.json", 'w') as f:
            json.dump(data, f)

        bot = Bot(id)
        self.bots[id] = bot

    @staticmethod
    async def rule():
        while True:
            print("Rule is running...")
            await asyncio.sleep(1)

    async def login_to_tt(self):
        for id, bot in self.bots.items():
            if bot.bot_status == 1 and id not in self.processing.keys():
                asyncio.create_task(bot.main())
                self.processing[id] = bot
                print(f"Task for bot {id} has been started.")
                break


class Server(Master):
    def __init__(self):
        super().__init__()

    async def find_task(self):
        task = 1
        while True:
            print(task)
            match task:
                case 1:  # create new bot
                    await self.new_bot()
                    print('bot created')
                    task += 1
                case 2:  # login bot to tt
                    await self.new_bot()
                    print('bot created')

                    task += 1
                case 3:  # create new bot
                    await self.new_bot()
                    print('bot created')

                    task += 1
                case 4:  # login bot to tt
                    await self.login_to_tt()
                    print('logined to tt')

                    task += 1
                case 5:  # login bot to tt
                    await self.login_to_tt()
                    print('logined to tt')
                    task += 1
                case 6:
                    await asyncio.sleep(1)
                    print("gegegegeg")

    async def create_link(self) -> str:
        return '@#!#13131'

    async def command_like(self):
        print("Command like received")


async def main():
    M = Master()
    S = Server()
    await asyncio.gather(
        M.rule(),
        S.find_task()
    )


if __name__ == "__main__":
    asyncio.run(main())
