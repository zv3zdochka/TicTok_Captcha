import json
import asyncio
import uuid
import random
import pickle
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as waiter


class Bot():
    def __init__(self, id, cookie):
        self.url, self.proxy, self.login_data, self.password_data, self.timeout, self.delay = None, None, None, None, None, None
        self.id = str(id)
        self.cookie = cookie
        self.load_config()
        self.status = 0  # 0 - not done 1 - in process 2 - done
        self.captcha = 0  # 0 - init 1 - open login 2 - select type 3 change type 4 - typped 5 - successful login
        self.chrome_options = self.setup_chrome_options()
        self.driver = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.bot_status = 1  # 0 -in process 1 - created and wait, 2 - logined and scrolling
        self.com = 'comment text'
        self.model = 0  # 0 swapping & like & comment, 1 - enter strim

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self.wait())
        else:
            loop.run_until_complete(self.wait())

    async def wait(self):
        while self.status == 1:
            await asyncio.sleep(3)

    async def stop_bot(self):
        pickle.dump(self.driver.get_cookies(), open(f"{self.id}.pkl", "wb"))


    async def to_strim(self, kink):
        self.model = 1
        self.driver.get(kink)

    def load_config(self):
        try:
            with open(fr"bots\{self.id}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.url = data['url']
                self.proxy = data['proxy']
                self.login_data = data['login']
                self.password_data = data['password']
                self.timeout = data['timeout']
                self.delay = data['delay']


        except Exception as e:
            exit(f"Fail on loading file {e}")

    def setup_chrome_options(self) -> Options:
        options = Options()
        options.add_argument(f'--proxy-server={self.proxy}')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--start-maximized")
        # options.add_argument("--headless=new")
        for cookie in self.cookie:
            self.driver.add_cookie(cookie)

        return options

    async def wait_for_captcha(self):
        loop = asyncio.get_event_loop()
        while self.captcha != 2:
            try:
                await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                           waiter.presence_of_element_located(
                                               (By.XPATH, '//*[@id="captcha_container"]/div')))
                print("Капча найдена")
                self.captcha = 1
                await asyncio.sleep(self.delay)
                self.driver.save_screenshot(f"{uuid.uuid4()}.png")
                await asyncio.sleep(self.delay)
                self.captcha = 2
                return True
            except Exception as e:
                print(f"Произошла ошибка при поиске капчи: {e}")
                return False

    async def first_captcha(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                           waiter.presence_of_element_located(
                                               (By.XPATH, '//*[@id="tiktok-verify-ele"]/div')))
                self.captcha = 1
                await asyncio.sleep(self.delay)
                self.driver.save_screenshot(f"{uuid.uuid4()}.png")
                await asyncio.sleep(self.delay)
                self.captcha = 2
                return True
            except Exception as e:
                print(f"Произошла ошибка при поиске капчи: {e}")
                return False

    async def login(self):
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                       waiter.presence_of_element_located(
                                           (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/div[1]/input')))

            login_field = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                     waiter.presence_of_element_located((By.XPATH,
                                                                                         '//*[@id="loginContainer"]/div[2]/form/div[1]/input')))
            login_field.send_keys(self.login_data)
            await asyncio.sleep(self.delay)
            password_field = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                        waiter.presence_of_element_located((By.XPATH,
                                                                                            '//*[@id="loginContainer"]/div[2]/form/div[2]/div/input')))
            password_field.send_keys(self.password_data)
            await asyncio.sleep(self.delay)

            login_button = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                      waiter.element_to_be_clickable(
                                                          (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/button')))
            login_button.click()
            await asyncio.sleep(5)
            try:
                login_button = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                          waiter.element_to_be_clickable(
                                                              (By.XPATH,
                                                               '//*[@id="loginContainer"]/div[2]/form/button')))
                login_button.click()
            except Exception:
                login_button = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                          waiter.element_to_be_clickable(
                                                              (By.XPATH,
                                                               '//*[@id="loginContainer"]/div[2]/form/button')))
                login_button.click()
            finally:
                await asyncio.sleep(3)
                return


        except Exception as e:
            print(f"Произошла ошибка при заполнении формы логина: {e}")

    async def clicker(self):
        loop = asyncio.get_event_loop()
        while True:
            if self.captcha == 1:
                await asyncio.sleep(self.delay)
                continue
            match self.status:
                case 0:
                    try:
                        login_button = await loop.run_in_executor(self.executor,
                                                                  WebDriverWait(self.driver, self.timeout).until,
                                                                  waiter.element_to_be_clickable(
                                                                      (By.XPATH, '//*[@id="header-login-button"]')))
                        login_button.click()
                        self.status = 1
                    except Exception as e:
                        print(f"Can't press login button with error {e}")
                        continue
                case 1:
                    try:
                        await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                   waiter.presence_of_element_located(
                                                       (By.XPATH, '//*[@id="login-modal"]/div[1]')))

                        await asyncio.sleep(self.delay)

                        change_login_type = await loop.run_in_executor(self.executor,
                                                                       WebDriverWait(self.driver, self.timeout).until,
                                                                       waiter.element_to_be_clickable((By.XPATH,
                                                                                                       '//*[@id="loginContainer"]/div/div/div/div[2]')))
                        change_login_type.click()
                        self.status = 2
                    except Exception as e:
                        print(f"Can't select login with error {e}")
                        continue
                case 2:
                    try:
                        change_login_type = await loop.run_in_executor(self.executor,
                                                                       WebDriverWait(self.driver, self.timeout).until,
                                                                       waiter.element_to_be_clickable((By.XPATH,
                                                                                                       '//*[@id="loginContainer"]/div/form/div[1]/a')))
                        change_login_type.click()
                        self.status = 3
                    except Exception as e:
                        print(f"Can't change login type with error {e}")
                        continue
                case 3:
                    try:
                        await self.login()
                        self.status = 4
                        await asyncio.sleep(10)
                    except Exception as e:
                        print(f"Can't login with error {e}")
                case 4:
                    loop = asyncio.get_event_loop()
                    print("here")
                    await asyncio.sleep(10)
                    try:
                        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, 5).until,
                                                         waiter.presence_of_element_located((By.XPATH,
                                                                                             '//*[@id="main-content-explore_page"]/div/div[2]/div/div[1]')))

                        but.click()
                    except Exception as e:
                        print('helly')
                        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                         waiter.presence_of_element_located((By.XPATH,
                                                                                             '/html/body/div[1]/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div/div/div[1]')))
                        but.click()
                    finally:
                        pass
                    print('video')
                    await asyncio.sleep(3)
                    self.status = 5

                    return

    async def online(self):
        while True:
            print(f"model {self.model}")
            match self.model:
                case 0:
                    t = random.randrange(2, 7)
                    await asyncio.sleep(t)
                    if t == random.randrange(1, 20):
                        await self.like()
                    # if t == random.randrange(1, 100):
                    #     await self.comment()
                    await self.swap()

                case 1:
                    pass  # strim
                case 2:
                    pass  # exit

            await asyncio.sleep(2)

    async def start_live(self):
        while True:
            print(f'status {self.status}')
            if self.status == 5:
                online_task = asyncio.create_task(self.online())
                await online_task
                return
            else:
                await asyncio.sleep(5)

    async def like(self):
        loop = asyncio.get_event_loop()
        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="app"]/div[2]/div[4]/div/div[2]/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/button[1]')))
        print("like")
        but.click()

    async def swap(self):
        loop = asyncio.get_event_loop()
        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="app"]/div[2]/div[4]/div/div[1]/button[3]')))
        print('swap')
        but.click()

    async def comment(self):
        loop = asyncio.get_event_loop()

        box = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="app"]/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/div')))
        box.send_keys(self.com)
        publ = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                          waiter.presence_of_element_located(
                                              (By.XPATH, '//*[@id="app"]/div[2]/div[4]/div/div[2]/div[2]/div/div[2]')))
        print("comment")
        publ.click()

    async def main(self):
        self.bot_status = 0
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        await asyncio.sleep(5)

        captcha_task = asyncio.create_task(self.wait_for_captcha())
        button_task = asyncio.create_task(self.clicker())
        online_task = asyncio.create_task(self.start_live())
        await captcha_task
        await button_task
        await online_task


if __name__ == "__main__":
    print()
    bot = Bot(123123)
    # bot.run()
