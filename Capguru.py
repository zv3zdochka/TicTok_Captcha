import asyncio

import requests
import base64
import re


class IncorrectNumberOfImages(Exception):
    def __init__(self, message="Expected 1 or 2 images, but received a different amount."):
        super().__init__(message)


class ServerError(Exception):
    def __init__(self, message="Server error. Please check the requests and response status."):
        super().__init__(message)


class KolesoCaptchaError(Exception):
    def __init__(self, message="Koleso captcha error."):
        super().__init__(message)


class PuzzleCaptchaError(Exception):
    def __init__(self, message="Puzzle captcha error."):
        super().__init__(message)


class ABCCaptchaError(Exception):
    def __init__(self, message="ABC captcha error."):
        super().__init__(message)


class Again:
    def __init__(self, message="Try another CAPTCHA."):
        super().__init__(message)


class Cap:
    def __init__(self, urls: list, captcha_type: str):
        self.key = "b18d37139a45ab6b89503345b4b521b3"
        self.captcha_type = captcha_type
        self.data = urls
        self.counter = 0
        self.payload = {'textinstructions': self.captcha_type, 'click': 'geetest', 'key': self.key, 'method': 'base64'}
        self.__preprocess_data()

    def __preprocess_data(self, again=False):
        if again:
            im1 = self.payload.get('body0')
            im2 = self.payload.get('body1')

            self.payload['body0'] = im2
            self.payload['body1'] = im1
            return

        if len(self.data) == 1:

            en_im_1 = base64.b64encode(requests.get(self.data[0]).content)
            self.payload['body'] = en_im_1

        elif len(self.data) == 2:
            en_im_1 = base64.b64encode(self.data[0].encode())
            en_im_2 = base64.b64encode(self.data[1].encode())

            self.payload['body0'] = en_im_1
            self.payload['body1'] = en_im_2

        else:
            raise IncorrectNumberOfImages

    async def __solve(self) -> str | int:
        r = requests.post("http://api.cap.guru/in.php", data=self.payload)

        await asyncio.sleep(8)

        if "OK" not in r.text:
            raise ServerError

        rt = r.text.split('|')
        url = 'http://api.cap.guru/res.php?key=' + self.key + '&id=' + rt[1]

        while self.counter != 3:
            response = requests.get(url).text
            if response == "CAPCHA_NOT_READY":
                await asyncio.sleep(2)
                continue
            elif response == "ERROR_CAPTCHA_UNSOLVABLE":
                self.counter += 1
                return -1
            elif "OK" in response:
                return response
            break
        return 0

    async def send(self):
        out = await self.__solve()
        while True:
            if out == -1:
                self.__preprocess_data(again=True)
                out = await self.__solve()
            elif out == 0:
                return 0
            else:
                # noinspection PyTypeChecker
                if 'w' not in out:
                    output = [(int(x), int(y)) for x, y in re.findall(r"x=(\d+),y=(\d+)", out)]
                else:
                    output = [(int(x), int(y), int(w)) for x, y, w in re.findall(r"x=(\d+),y=(\d+),w=(\d+)", out)]
                break

        if self.captcha_type == 'koleso':
            if len(output) != 1:
                raise KolesoCaptchaError
            return max(output[0])

        elif self.captcha_type == "abc":
            if len(output[0]) != 2:
                raise ABCCaptchaError
            return output

        elif self.captcha_type == "slider":
            if len(output[0]) != 3:
                raise PuzzleCaptchaError
            return output


if __name__ == "__main__":
    url1 = 'https://p19-rc-captcha-useast2a.tiktokcdn-eu.com/tos-useast2a-i-447w7jt563-euttp/8ff1d4f696084cad95f6ddbdaa0809de~tplv-447w7jt563-2.jpeg'

    url2 = 'https://p19-rc-captcha-useast2a.tiktokcdn-eu.com/tos-useast2a-i-447w7jt563-euttp/33caed8d2f0546d2b728ab32ddaa9e75~tplv-447w7jt563-2.jpeg'

    puzzle = rf"https://p16-rc-captcha-useast2a.tiktokcdn-eu.com/tos-useast2a-i-447w7jt563-euttp/b75bd59c5c614ce2a250ff0dcf4879e3~tplv-447w7jt563-2.jpeg"
    puzzle_1 = rf"https://p16-rc-captcha-useast2a.tiktokcdn-eu.com/tos-useast2a-i-447w7jt563-euttp/32595089eb1a4d67bbe86d674dac72b7~tplv-447w7jt563-2.jpeg"
    abc = rf"https://p16-security-sg.ibyteimg.com/img/security-captcha-oversea-singapore/3d_c0899f7bd5ce8470ae4fa7bda6df3e10345f44d7_1_2.jpg~tplv-obj.image"

    img = [
        puzzle_1
    ]
    C = Cap(img, 'slider')
    print(asyncio.run(C.send()))
