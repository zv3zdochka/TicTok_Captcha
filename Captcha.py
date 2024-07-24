import json
import asyncio
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as waiter
from Bot import call_operator


class Bot():
    def __init__(self, id):
        self.url, self.proxy, self.login_data, self.password_data, self.timeout, self.delay, self.cookie = None, None, None, None, None, None, None
        self.id = str(id)
        self.load_config()
        self.status = 0  # 0 - not done 1 - in process 2 - done
        self.captcha = 0  # 0 - init 1 - open login 2 - select type 3 change type 4 - success
        self.chrome_options = self.setup_chrome_options()
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.driver.get("https://ya.ru/")
        self.status = 1 # 0 Offline, 1 - wait, 2 - scrolling
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self.wait())
        else:
            loop.run_until_complete(self.wait())

    async def wait(self):
        while self.status == 1:
            await asyncio.sleep(3)
            print('wait')

    def stop_bot(self):
        pass


    def load_config(self):
        try:
            with open(self.id + '.json', 'r', encoding='utf-8') as f:
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
        return options

    async def get_link(self):
        return self.create_link()

    async def wait_for_captcha(self):
        loop = asyncio.get_event_loop()
        while self.captcha != 2:
            try:
                await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                           waiter.presence_of_element_located(
                                               (By.XPATH, '//*[@id="captcha_container"]/div')))

                print("Капча найдена")

                self.captcha = 1

                await call_operator(await self.get_link())

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
                    except Exception as e:
                        print(f"Can't login with error {e}")
                case 4:
                    await asyncio.sleep(50)
                    print("Ждем команд")
                    await asyncio.sleep(self.timeout)
                    return

    async def like(self):
        loop = asyncio.get_event_loop()
        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="main-content-homepage_hot"]/div[1]/div[1]/div/div/div[2]/button[1]')))
        but.click()

    async def comment(self):
        loop = asyncio.get_event_loop()
        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="main-content-homepage_hot"]/div[1]/div[1]/div/div/div[2]/button[2]')))
        but.click()
        box = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="app"]/div[2]/div[4]/div/div[2]/div[2]/div/div[1]/div')))
        box.send_keys(self.com)
        publ = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                          waiter.presence_of_element_located(
                                              (By.XPATH, '//*[@id="app"]/div[2]/div[4]/div/div[2]/div[2]/div/div[2]')))
        publ.click()

    async def main(self):
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        await asyncio.sleep(5)

        captcha_task = asyncio.create_task(self.wait_for_captcha())
        button_task = asyncio.create_task(self.clicker())

        await captcha_task
        #await button_task

    def run(self):
        try:
            asyncio.run(self.main())
        finally:
            self.driver.quit()


if __name__ == "__main__":
    bot = Bot(123123)
    # bot.run()


# //*[@id="tiktok-verify-ele"]/div box с капчей
#
# //*[@id="verify-bar-close"] его можно закрыть

