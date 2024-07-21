import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
captcha = 0
# 0 - init 1 - open login 2 - select type 3 change type 4 - success

# Settings
chrome_options = Options()
# chrome_options.add_argument(f'--proxy-server={proxy}')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-plugins-discovery')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# Initialize driver
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1500, 850)
driver.get(url)

# ThreadPoolExecutor for running blocking selenium operations
executor = ThreadPoolExecutor(max_workers=2)


async def wait_for_captcha():
    loop = asyncio.get_event_loop()
    try:
        element = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                             EC.presence_of_element_located((By.XPATH, '//*[@id="tiktok-verify-ele"]')))
        print("Капча найдена")

        await asyncio.sleep(delay)

        # Делаем скриншот страницы
        screenshot_path = "captcha_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Скриншот страницы сохранен в файл {screenshot_path}")

        return True
    except Exception as e:
        print(f"Произошла ошибка при поиске капчи: {e}")
        return False


async def login():
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                   EC.presence_of_element_located(
                                       (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/div[1]/input')))
        print("Форма логина найдена")

        login_field = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                 EC.presence_of_element_located(
                                                     (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/div[1]/input')))
        login_field.send_keys(login_data)
        print("Логин заполнен")
        await asyncio.sleep(delay)
        password_field = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                    EC.presence_of_element_located((By.XPATH,
                                                                                    '//*[@id="loginContainer"]/div[2]/form/div[2]/div/input')))
        password_field.send_keys(password_data)
        print("Пароль заполнен")
        await asyncio.sleep(delay)

        login_button = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                  EC.element_to_be_clickable(
                                                      (By.XPATH, '//*[@id="loginContainer"]/div[2]/form/button')))
        login_button.click()
        print("Кнопка входа нажата")
    except Exception as e:
        print(f"Произошла ошибка при заполнении формы логина: {e}")


async def wait_for_button():
    loop = asyncio.get_event_loop()
    while True:
        if await loop.run_in_executor(executor, lambda: driver.find_elements(By.XPATH, '//*[@id="tiktok-verify-ele"]')):
            screenshot_path = "captcha_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Скриншот страницы сохранен в файл {screenshot_path}")

        try:
            login_button = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                      EC.element_to_be_clickable(
                                                          (By.XPATH, '//*[@id="header-login-button"]')))
            login_button.click()
            print("Кнопка нажата")

            await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                       EC.presence_of_element_located((By.XPATH, '//*[@id="login-modal"]/div[1]')))
            print("Элемент login-modal найден")

            await asyncio.sleep(delay)

            change_login_type = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                           EC.element_to_be_clickable(
                                                               (By.XPATH,
                                                                '//*[@id="loginContainer"]/div/div/div/div[2]')))
            change_login_type.click()
            print("Вторая кнопка нажата")

            change_login_type = await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                                           EC.element_to_be_clickable(
                                                               (By.XPATH,
                                                                '//*[@id="loginContainer"]/div/form/div[1]/a')))
            change_login_type.click()

            print("Третья кнопка нажата")

            await login()

            await asyncio.sleep(50)
            print("here")
            await asyncio.sleep(timeout)
            return
        except Exception as e:
            print(f"Произошла ошибка при поиске или нажатии кнопки: {e}")


async def main():
    captcha_task = asyncio.create_task(wait_for_captcha())
    button_task = asyncio.create_task(wait_for_button())

    await captcha_task
    await button_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        driver.quit()
