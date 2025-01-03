## Скритп Олежи

### Обзор

Этот скрипт представляет собой бота для автоматического логина в TikTok с использованием Selenium. Если бот находит CAPTCHA, он вызывает функцию `call_operator`, которая рассылает CAPTCHA вызов операторам. Операторы получают ссылку для решения CAPTCHA. 

### Функциональные возможности

- Автоматический логин в TikTok.
- Обнаружение CAPTCHA и вызов функции для решения CAPTCHA операторами.
- Возможность ставить лайки и писать комментарии.

### Как работает код

1. **Чтение конфигурации**:
    - Загружаются настройки из файла `config.json`, включая URL, прокси, логин, пароль и тайм-ауты.

2. **Настройки Selenium**:
    - Настраиваются параметры для браузера Chrome, включая прокси и различные опции для отключения уведомлений и плагинов.

3. **Инициализация драйвера**:
    - Инициализируется экземпляр браузера Chrome и открывается указанный URL.

4. **Асинхронное ожидание CAPTCHA**:
    - Функция `wait_for_captcha` ждет появления CAPTCHA на странице.
    - Если CAPTCHA найдена, вызывается функция `call_operator` для рассылки вызова операторам с ссылкой на CAPTCHA.

5. **Асинхронный логин**:
    - Функция `login` выполняет ввод логина и пароля на странице и нажимает кнопку входа.

6. **Асинхронный кликер**:
    - Функция `clicker` обрабатывает шаги логина, переходя от нажатия кнопки логина до смены типа логина и ввода учетных данных.

7. **Основной цикл**:
    - Функция `main` запускает задачи для ожидания CAPTCHA и обработки логина.

### Как запустить

1. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

2. Создайте файл `config.json` в той же директории, где находится скрипт:
    ```json
    {
        "url": "https://www.tiktok.com/login",
        "proxy": "http://proxyserver:port",
        "login": "your_login",
        "password": "your_password",
        "timeout": 30,
        "delay": 5
    }
    ```
