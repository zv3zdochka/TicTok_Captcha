# README

## Описание

Этот скрипт автоматизирует процесс входа в TikTok с использованием Selenium. В случае появления капчи скрипт делает скриншот и готов передать его на сервер для дальнейшей работы, а также предоставляет возможность решить капчу оператору на месте.

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone <URL вашего репозитория>
   cd <название директории>
   ```

2. Установите необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Конфигурация

Создайте файл `config.json` в корне проекта со следующим содержанием:
```json
{
    "url": "https://www.tiktok.com/login",
    "proxy": "http://your-proxy-server:port",
    "login": "your-login",
    "password": "your-password",
    "timeout": 30,
    "delay": 5
}
```

## Принцип работы

1. **Инициализация**: Настраиваем Selenium WebDriver с указанным прокси и опциями.
   ```python
   chrome_options = Options()
   chrome_options.add_argument(f'--proxy-server={proxy}')
   driver = webdriver.Chrome(options=chrome_options)
   driver.get(url)
   ```

2. **Обработка капчи**: Асинхронная функция `wait_for_captcha` ожидает появления капчи, делает скриншот и предоставляет оператору возможность ее решить.
   ```python
   async def wait_for_captcha():
       await loop.run_in_executor(executor, WebDriverWait(driver, timeout).until,
                                  waiter.presence_of_element_located((By.XPATH, '//*[@id="captcha_container"]/div')))
       driver.save_screenshot(f"{uuid.uuid4()}.png")
       await asyncio.sleep(delay)
   ```

3. **Вход в систему**: Асинхронная функция `login` вводит данные логина и пароля.
   ```python
   async def login():
       login_field.send_keys(login_data)
       password_field.send_keys(password_data)
       login_button.click()
   ```

4. **Главный цикл**: Функция `clicker` выполняет последовательность шагов для входа, включая нажатие кнопок и переключение типов входа.
   ```python
   async def clicker():
       while True:
           match status:
               case 0:
                   login_button.click()
               case 1:
                   change_login_type.click()
               case 2:
                   change_login_type.click()
               case 3:
                   await login()
   ```

5. **Основная функция**: Запускает задачи для обработки капчи и входа.
   ```python
   async def main():
       captcha_task = asyncio.create_task(wait_for_captcha())
       button_task = asyncio.create_task(clicker())
       await captcha_task
       await button_task
   ```

## Запуск

Запустите скрипт:
```bash
python script_name.py
```

## Требования

- Python 3.7+
- Selenium
- asyncio
- json
- concurrent.futures
- webdriver_manager

## Примечания

- Убедитесь, что `config.json` заполнен правильно перед запуском скрипта.
- Скрипт рассчитан на работу с капчей и может потребовать доработки в зависимости от изменений на стороне TikTok.
