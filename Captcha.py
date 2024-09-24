import json
import asyncio
import random
from asyncio import Queue
import pickle
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as waiter
from selenium_authenticated_proxy import SeleniumAuthenticatedProxy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from Capguru import Cap


# noinspection PyAsyncCall

class IncorrectNumberOfCaptchaImages(Exception):
    def __init__(self, message="Incorrect number of images registered in CAPTCHA."):
        super().__init__(message)


class Bot:
    def __init__(self, id, cookie):
        self.url, self.proxy, self.login_data, self.password_data, self.timeout, self.delay = None, None, None, None, None, None
        self.id = str(id)
        self.cookie = cookie
        self.load_config()
        self.status = 0  # 0 - not done 1 - in process 2 - done
        self.captcha = 0  # 0 - init 1 - open login 2 - select type 3 change type 4 - typped 5 - successful login
        self.chrome_options = self.setup_chrome_options()
        self.driver = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.bot_status = 1  # 0 -in process 1 - created and wait, 2 - logined and scrolling 3 - on strim
        self.com = 'comment text'
        self.strim_link = "https://www.tiktok.com/@bang_1one_96/live"
        self.proxy_login, self.proxy_password, self.proxy_cr = None, None, None
        self.model = 0  # 0 swapping & like & comment, 1 - on strim
        self.captcha_type = None
        self.task_queue = Queue()

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self.wait())
        else:
            loop.run_until_complete(self.wait())

    def load_config(self) -> None:
        try:
            with open(fr"bots\{self.id}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.url = data['url']
                self.login_data = data['login']
                self.password_data = data['password']
                self.timeout = data['timeout']
                self.delay = data['delay']
                self.proxy_login = data['proxy_login']
                self.proxy_password = data['proxy_password']
                self.proxy_cr = data['proxy_cr']

        except Exception as e:
            exit(f"Fail on loading config bot file: {e}")

    def setup_chrome_options(self) -> Options:

        options = Options()

        options.add_argument('--disable-infobars')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('disable-notifications')

        options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument("--start-maximized")
        # options.add_argument("--headless=new") #  don't change new, because it'll break the proxy

        proxy_helper = SeleniumAuthenticatedProxy(
            proxy_url=f"http://{self.proxy_login}:{self.proxy_password}@{self.proxy_cr}")

        # Enrich Chrome options with proxy authentication
        proxy_helper.enrich_chrome_options(options)

        # for cookie in self.cookie:
        #     self.driver.add_cookie(cookie)

        return options

    async def add_task(self, task):
        """Асинхронно добавляем задачу в очередь."""
        await self.task_queue.put(task)

    def get_queue_length(self):
        """Возвращает длину очереди задач."""
        return self.task_queue.qsize()

    async def load_error_check(self):
        """
        proxy error
        :return:
        """
        loop = asyncio.get_event_loop()
        while True:
            try:
                print("herer")
                login_button = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                                          waiter.element_to_be_clickable(
                                                              (By.XPATH,
                                                               '/html/body/tiktok-cookie-banner//div/div[2]/button[2]')))
                print("found")
                await asyncio.sleep(1)
                login_button.click()
                print("cookie agree")
                await asyncio.sleep(5)

            except TimeoutException:
                pass

    async def wait_for_captcha(self):
        loop = asyncio.get_event_loop()
        while True:
            try:
                # Ожидание появления капчи
                await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                           waiter.presence_of_element_located(
                                               (By.CLASS_NAME, "captcha_verify_container")))
                print("Найдена CAPTCHA")
                await asyncio.sleep(3)

                # Получение всех элементов с атрибутом src
                elements_with_src = self.driver.find_elements(By.XPATH, '//*[@src]')

                src_urls = []
                for element in elements_with_src:
                    src = element.get_attribute('src')
                    if "captcha" in src and (src.endswith(".jpeg") or src.endswith('.jpg') or src.endswith(".image")):
                        src_urls.append(src)
                        print(f"Найден src: {src}")

                # Определение типа капчи
                if len(src_urls) == 2:
                    print('koleso')
                    self.captcha_type = 'koleso'
                    pass
                    C = Cap(src_urls, 'koleso')

                elif len(src_urls) == 1:
                    if src_urls[0].endswith(".image"):
                        print('abc')
                        self.captcha_type = 'abc'
                        C = Cap(src_urls, 'abc')
                    else:
                        print('slider')
                        self.captcha_type = 'slider'
                        C = Cap(src_urls, 'slider')
                else:
                    raise Exception("Неправильное количество изображений капчи")

                # Отправляем капчу на решение
                try:
                    answer = await C.send()
                    print(f"Ответ на капчу: {answer}")
                except Exception as e:
                    print(f"Ошибка при решении капчи: {e}")
                    continue

                if answer == 0:
                    n = 0
                    return True
                    # Обновить капчу и попробовать снова

                # В зависимости от типа капчи решаем её
                if self.captcha_type == "koleso":
                    await self.drag_slider(int(answer))
                    return

                elif self.captcha_type == "abc":
                    captcha_element = self.driver.find_element(By.ID, "captcha-verify-image")
                    captcha_rect = captcha_element.location

                    # print(f"Координаты капчи: {captcha_rect}")
                    # print(f"Размеры капчи: {captcha_element.size}")
                    #
                    # actions = ActionChains(self.driver)
                    # actions.move_by_offset(captcha_element.size[0] / 2 + captcha_rect[0],
                    #                        captcha_element.size[1] / 2 + captcha_rect[1]).click().perform()
                    # await asyncio.sleep(0.5)

                    for i in answer:
                        actions = ActionChains(self.driver)
                        actions.move_by_offset(captcha_rect.get('x') + i[0],
                                               captcha_rect.get('y') + i[1]).click().perform()
                        await asyncio.sleep(0.5)
                    return

                elif self.captcha_type == "slider":
                    await self.drag_slider(answer[0][0] - 100)
                    return

                await asyncio.sleep(self.delay)
                self.captcha = 2
                return

            except Exception as e:
                print(f"Ошибка при ожидании капчи: {e}")
                await asyncio.sleep(self.delay)

    async def drag_slider(self, x: int):
        slider = self.driver.find_element(By.CLASS_NAME, "secsdk-captcha-drag-icon")
        ActionChains(self.driver).click_and_hold(slider).perform()

        for _ in range(11):
            ActionChains(self.driver).move_by_offset(x // 11, 0).perform()

        ActionChains(self.driver).move_by_offset(14, 0).perform()
        ActionChains(self.driver).move_by_offset(-10, 0).perform()

        ActionChains(self.driver).move_by_offset(5, 0).perform()

        ActionChains(self.driver).move_by_offset(-9, 0).perform()

        ActionChains(self.driver).move_by_offset(x % 11, 0).release().perform()
        return

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
                await asyncio.sleep(15)
                # solving CAPTCHA
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
                    except Exception as e:
                        print(f"Can't login with error {e}")
                case 4:
                    # await asyncio.sleep(1100)
                    loop = asyncio.get_event_loop()
                    print("find to swap")
                    await asyncio.sleep(2)
                    while True:
                        try:
                            await loop.run_in_executor(self.executor, WebDriverWait(self.driver, 10).until,
                                                       waiter.presence_of_element_located((By.XPATH,
                                                                                           '//*[@id="app-header"]/div/div[3]/div[3]')))
                            print("done")
                            break
                        except Exception as e:
                            pass
                    print('start swaping videos')
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
                        await self.swap_like()
                    if t == random.randrange(1, 100):
                        await self.swap_comment()
                    await self.swap()

                case 1:
                    # on strim
                    print("On strim")
                    # await asyncio.sleep(1)
                    # await self.strim_like()
                    # await self.strim_comment()
                case 2:
                    pass  # exit

            await asyncio.sleep(2)

    async def wait(self):
        while self.status == 1:
            await asyncio.sleep(3)

    async def stop_bot(self):
        pickle.dump(self.driver.get_cookies(), open(f"{self.id}.pkl", "wb"))
        self.driver.quit()
        await asyncio.sleep(1)

    async def enter_strim(self):
        self.model = 1
        self.driver.get(self.strim_link)
        await asyncio.sleep(15)

    async def start_live(self):
        while True:
            print(f'status {self.status}')
            if self.status == 5:
                online_task = asyncio.create_task(self.online())
                await online_task
                return
            else:
                await asyncio.sleep(1)

    async def swap_like(self):
        loop = asyncio.get_event_loop()
        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="app"]/div[2]/div[4]/div/div[2]/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/button[1]')))
        print("like")
        but.click()
        await asyncio.sleep(1)

    async def strim_like(self):
        loop = asyncio.get_event_loop()
        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="tiktok-live-main-container-id"]/div[4]/div[2]/div/div[2]/div[3]/div[2]/div[1]/div[4]')))
        print("like")
        for _ in range(20):
            but.click()
        await asyncio.sleep(1)

    async def swap(self):
        loop = asyncio.get_event_loop()
        but = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="app"]/div[2]/div[4]/div/div[1]/button[3]')))
        print('swap')
        but.click()
        await asyncio.sleep(1)

    async def swap_comment(self):
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
        await asyncio.sleep(1)

    async def strim_comment(self):
        loop = asyncio.get_event_loop()

        box = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                         waiter.presence_of_element_located((By.XPATH,
                                                                             '//*[@id="tiktok-live-main-container-id"]/div[4]/div[2]/div/div[2]/div[3]/div[4]/div[1]/div/div[1]/div')))
        box.send_keys("Testing comment")
        publ = await loop.run_in_executor(self.executor, WebDriverWait(self.driver, self.timeout).until,
                                          waiter.presence_of_element_located(
                                              (By.XPATH,
                                               '//*[@id="tiktok-live-main-container-id"]/div[4]/div[2]/div/div[2]/div[3]/div[4]/div[2]')))
        print("comment")
        publ.click()
        await asyncio.sleep(1)

    # noinspection PyAsyncCall

    async def start_bot(self):
        self.bot_status = 0
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.delete_all_cookies()
        self.driver.get(self.url)
        await asyncio.sleep(3)

        asyncio.create_task(self.wait_for_captcha())
        clicker_task = asyncio.create_task(self.clicker())
        asyncio.create_task(self.start_live())
        await asyncio.gather(clicker_task)
        print("We end on login")
        await asyncio.sleep(1)
        return

    async def process_task(self, task):
        print(task)
        func_id = int(task.get('args').get("task_action"))
        match func_id:
            case 9:
                print("Starting bot")
                try:
                    await self.start_bot()
                except Exception:
                    print("Can't start bot")
                print("Bot started")

            case 15:
                print("Going on strim")
                try:
                    await self.enter_strim()
                except Exception:
                    print("cant push bot on strim")
                print('On strim')
            case 5:
                # wait
                pass
            case 3:
                try:
                    await self.strim_like()
                except Exception:
                    print("can't like")
                pass
            case 11:
                try:
                    await self.stop_bot()
                except Exception:
                    print("can't stop bot")
                pass

    async def run(self):
        """Асинхронный цикл бота для проверки и выполнения задач."""
        while True:
            if not self.task_queue.empty():
                task = await self.task_queue.get()
                print(task)
                await self.process_task(task)
            else:
                await asyncio.sleep(1)
