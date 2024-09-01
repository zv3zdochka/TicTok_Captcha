def __solve_captcha_if_need(self, timeout: float) -> None:
    """Solves captcha if it appears

    Args:
        timeout (float): captcha waiting time.
    """

    try:
        captcha_container = self.__wait_load_element((By.CLASS_NAME, "captcha_verify_container"), timeout)
    except TimeoutException as e:
        return

    if not captcha_container.is_displayed():
        return

    self.__wait_load_element((By.TAG_NAME, "img"))
    time.sleep(2)

    image_urls = []
    for image in captcha_container.find_elements(By.TAG_NAME, "img"):
        image_urls.append(image.get_attribute("src"))

    if len(image_urls) == 1:
        type_of_captcha = "abc"
    else:
        type_of_captcha = "koleso"

    CaptchaSolver(self.driver).solve_captcha(type_of_captcha, image_urls)
    print("Капча решена")


def __wait_load_element(self, locator: Tuple[str, str], timeout: float = 20.0) -> WebElement:
    """Waiting for the element to load.

    Args:
        locator (Tuple[str, str]): used to find the element returns the WebElement once it is located.
        timeout (float, optional): number of seconds before timing out. Defaults to 20.0.

    Returns:
        WebElement: found element.

    Raises:
    --------
        **TimeoutException**: failed to find element.
    """

    return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))