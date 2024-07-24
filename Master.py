from Captcha import Bot
import asyncio
import uuid
import json


class Master:
    def __init__(self):
        self.bots = {}

    async def new_bot(self):
        id = uuid.uuid4()
        print(id)

        data = {"url": "https://tiktok.com",
                "id": str(id),
                "proxy": "35.185.196.38:3128",
                "login": "captchatester123",
                "password": "HelloWorld123!",
                "timeout": 60,
                "delay": 5}

        with open(f"{str(id)}.json", 'w') as f:
            json.dump(data, f)

        self.bots[id] = Bot(id)
        print(self.bots)

    async def rule(self):
        while True:
            print("Rule is running...")
            await asyncio.sleep(1)


class Server(Master):
    def __init__(self):
        super().__init__()

    async def find_task(self):
        task = 1
        while True:
            # server request
            await asyncio.sleep(3)
            print(task)
            match task:
                case 1:  # create new bot
                    print('1')
                    await self.new_bot()
                    task += 1
                case 2:  # login new bot
                    print('2')
                    await self.new_bot()
                    task += 1
                case 3:
                    pass

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
