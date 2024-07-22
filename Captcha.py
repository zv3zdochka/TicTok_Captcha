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

# json
with open('config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    url = data['url']
    proxy = data['proxy']
    login_data = data['login']
    password_data = data['password']
    timeout = data['timeout']
    delay = data['delay']
    del data

status = 0
# 0 - not done 1 - in process 2 - done
captcha = 0
# 0 - init 1 - open login 2 - select type 3 change type 4 - success


# Settings
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server={proxy}')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-plugins-discovery')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--start-maximized")

# Initialize driver
driver = webdriver.Chrome(options=chrome_options)
driver.delete_all_cookies()
driver.get(url)
time.sleep(5)
# ThreadPoolExecutor for running blocking selenium operations
executor = ThreadPoolExecutor(max_workers=2)


async def wait_for_captcha():
    global captcha
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                   waiter.presence_of_element_located(
                                       (By.XPATH, '//*[@id="captcha_container"]/div')))
        print("Капча найдена")
        captcha = 1

        await asyncio.sleep(delay)

        driver.save_screenshot(f"{uuid.uuid4()}.png")


        # wait operator to do captcha
        await asyncio.sleep(delay)



        captcha = 2

        return True
    except Exception as e:
        print(f"Произошла ошибка при поиске капчи: {e}")
        return False


async def login():
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                   waiter.presence_of_element_located(
                                       (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/div[1]/input')))

        login_field = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                 waiter.presence_of_element_located(
                                                     (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/div[1]/input')))
        login_field.send_keys(login_data)
        await asyncio.sleep(delay)
        password_field = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                    waiter.presence_of_element_located((By.XPATH,
                                                                                        '//*[@id="loginContainer"]/div[2]/form/div[2]/div/input')))
        password_field.send_keys(password_data)
        await asyncio.sleep(delay)

        login_button = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                  waiter.element_to_be_clickable(
                                                      (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/button')))
        login_button.click()
    except Exception as e:
        print(f"Произошла ошибка при заполнении формы логина: {e}")


async def clicker():
    global status
    loop = asyncio.get_event_loop()
    while True:
        if captcha == 1:
            await asyncio.sleep(delay)
            continue
        match status:
            case 0:
                try:
                    login_button = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                              waiter.element_to_be_clickable(
                                                                  (By.XPATH, '//*[@id="header-login-button"]')))
                    login_button.click()
                    status = 1
                except Exception as e:
                    print(f"Can't press login button with error {e}")
                    continue
            case 1:
                try:
                    await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                               waiter.presence_of_element_located(
                                                   (By.XPATH, '//*[@id="login-modal"]/div[1]')))

                    await asyncio.sleep(delay)

                    change_login_type = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                                   waiter.element_to_be_clickable(
                                                                       (By.XPATH,
                                                                        '//*[@id="loginContainer"]/div/div/div/div[2]')))
                    change_login_type.click()
                    status = 2
                except Exception as e:
                    print(f"Can't select login with error {e}")
                    continue
            case 2:
                try:
                    change_login_type = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                                   waiter.element_to_be_clickable(
                                                                       (By.XPATH,
                                                                        '//*[@id="loginContainer"]/div/form/div[1]/a')))
                    change_login_type.click()
                    status = 3
                except Exception as e:
                    print(f"Can't change login type with error {e}")
                    continue

            case 3:
                try:
                    await login()
                    status = 4
                except Exception as e:
                    print(f"Can't login with error {e}")
            case 4:

                await asyncio.sleep(50)
                print("here")
                await asyncio.sleep(timeout)
                return


async def main():
    captcha_task = asyncio.create_task(wait_for_captcha())
    button_task = asyncio.create_task(clicker())

    await captcha_task
    await button_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        driver.quit()
