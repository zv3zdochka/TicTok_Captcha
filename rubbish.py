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
    maintime = data['maintime']
    timeauth = data['timeauth']
    timestream = data['timestream']
    timeexit = data['timeexit']
    del data

# Settings
chrome_options = Options()
#chrome_options.add_argument(f'--proxy-server={proxy}')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-plugins-discovery')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# Initialize
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1500, 850)
driver.get(url)

# ThreadPoolExecutor for running blocking selenium operations
executor = ThreadPoolExecutor(max_workers=2)


async def captcha():
    loop = asyncio.get_event_loop()
    try:
        element = await loop.run_in_executor(executor, WebDriverWait(driver, maintime).until,
                                             EC.presence_of_element_located((By.XPATH, '//*[@id="tiktok-verify-ele"]')))
        print("Капча найдена")

        # Ожидание полной загрузки страницы перед сохранением HTML
        await asyncio.sleep(2)

        # Получаем HTML код всей страницы
        page_html = driver.page_source

        # Сохраняем HTML код в файл
        with open("captcha_page.html", "w", encoding='utf-8') as file:
            file.write(page_html)

        print("HTML код страницы сохранен в файл captcha_page.html")
        return True
    except Exception as e:
        print(f"Произошла ошибка при поиске капчи: {e}")
        return False


async def wait_for_button():
    loop = asyncio.get_event_loop()
    while True:
        if await loop.run_in_executor(executor, lambda: driver.find_elements(By.XPATH, '//*[@id="tiktok-verify-ele"]')):
            print("Капча найдена, остановка ожидания кнопки")
            return
        try:
            login_button = await loop.run_in_executor(executor, WebDriverWait(driver, maintime).until,
                                                 EC.element_to_be_clickable(
                                                     (By.XPATH, '//*[@id="header-login-button"]')))
            login_button.click()
            print("Кнопка нажата")

            # Ждем появления элемента с xpath '//*[@id="login-modal"]/div[1]'
            await loop.run_in_executor(executor, WebDriverWait(driver, maintime).until,
                                       EC.presence_of_element_located((By.XPATH, '//*[@id="login-modal"]/div[1]')))
            print("Элемент login-modal найден")

            # Ждем 2 секунды
            await asyncio.sleep(2)

            # Нажимаем кнопку с xpath '//*[@id="loginContainer"]/div/div/div/div[4]'
            change_login_type = await loop.run_in_executor(executor, WebDriverWait(driver, maintime).until,
                                                       EC.element_to_be_clickable(
                                                           (By.XPATH, '//*[@id="loginContainer"]/div/div/div/div[2]')))
            change_login_type.click()
            print("Вторая кнопка нажата")

            change_login_type = await loop.run_in_executor(executor, WebDriverWait(driver, maintime).until,
                                                       EC.element_to_be_clickable(
                                                           (By.XPATH, '//*[@id="loginContainer"]/div/form/div[1]/a')))
            change_login_type.click()


            print("Третья кнопка нажата")



            await asyncio.sleep(50)

            return
        except Exception as e:
            print(f"Произошла ошибка при поиске или нажатии кнопки: {e}")


async def main():
    #captcha_task = asyncio.create_task(wait_for_captcha())
    button_task = asyncio.create_task(wait_for_button())

    #await captcha_task
    await button_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        driver.quit()
