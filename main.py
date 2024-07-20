import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Чтение JSON из файла
with open('config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Извлечение переменных
url = data['url']
proxy = data['proxy']
email = data['email']
password = data['password']
urlstream = data['urlstream']
comment = data['comment']
maintime = data['maintime']
timeauth = data['timeauth']
timestream = data['timestream']
timeexit = data['timeexit']
# Настройки браузера
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server={proxy}')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-plugins-discovery')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# Инициализировать браузер
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1920, 1080)
driver.get(url)
time.sleep(maintime)

element_found = False

while True:
    try:
        # Пытаемся найти нужный элемент
        element = driver.find_element(By.XPATH, '//*[@id="header-login-button"]')
        element_found = True
        print("Элемент найден и страница полностью загружена")
        break
    except:

        time.sleep(maintime)

# authorization

driver.find_element(By.XPATH, '//*[@id="header-login-button"]').click()
time.sleep(5)

patha = '//*[@id="loginContainer"]/div/div/div[1]/div[2]/div[2]'
driver.find_element(By.XPATH, patha).click()
time.sleep(5)
pathb = '//*[@id="loginContainer"]/div/form/div[1]/a'
driver.find_element(By.XPATH, pathb).click()
time.sleep(8)

emailauth = driver.find_element(By.NAME, "username")
emailauth.send_keys(email)
pathc = '//*[@id="loginContainer"]/div[2]/form/div[2]/div/input'
passwordauth = driver.find_element(By.XPATH, pathc)
passwordauth.send_keys(password)

time.sleep(5)

pathd = '//*[@id="loginContainer"]/div[2]/form/button'
driver.find_element(By.XPATH, pathd).click()
time.sleep(timeauth)

driver.get(urlstream)
time.sleep(15)
# лайки
driver.get(urlstream)
time.sleep(timestream)  # Ждем загрузки страницы

element_found1 = False

while True:
    try:
        # Пытаемся найти нужный элемент
        element = driver.find_element(By.XPATH,
                                      '//*[@id="tiktok-live-main-container-id"]/div[2]/div[2]/div/div[2]/div[3]/div/div[1]/div[4]/div[2]/div')
        element_found1 = True
        print("Элемент найден и страница полностью загружена")
        break
    except:

        time.sleep(timestream)

driver.find_element(By.XPATH,
                    '//*[@id="tiktok-live-main-container-id"]/div[2]/div[2]/div/div[2]/div[3]/div/div[1]/div[4]/div[2]/div').click()
time.sleep(3)

# комментарий

driver.find_element(By.XPATH,
                    '//*[@id="tiktok-live-main-container-id"]/div[2]/div[2]/div/div[2]/div[3]/div/div[3]/div[1]/div/div[1]/div').click()
key = driver.find_element(By.XPATH,
                          '//*[@id="tiktok-live-main-container-id"]/div[2]/div[2]/div/div[2]/div[3]/div/div[3]/div[1]/div/div[1]/div')
key.send_keys({comment})
driver.find_element(By.XPATH,
                    '//*[@id="tiktok-live-main-container-id"]/div[2]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]').click()
time.sleep(5)
# подписка

original_link = urlstream


# Функция для редактирования ссылки
def edit_link(link):
    parts = link.split('/')
    if 'live' in parts:
        parts.remove('live')
    return '/'.join(parts)


# Обработанная ссылка
edited_link = edit_link(original_link)
driver.get(edited_link)
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="main-content-others_homepage"]/div/div[1]/div[1]/div/div/div/button').click()
time.sleep(5)

# выход
driver.get("https://www.tiktok.com/passport/web/logout")
time.sleep(timeexit)
