import requests
import base64
import asyncio


class IncorrectNumberOfImages(Exception):
    pass


class CaptchaError(Exception):
    pass


class Cap:
    def __init__(self, url: list, type_of_captcha: str):
        self.key = "b18d37139a45ab6b89503345b4b521b3"
        if len(url) not in [1, 2]:
            raise IncorrectNumberOfImages
        if len(url) == 1:
            self.url = url[0]
            self.url_1 = None
        else:
            self.url = url[0]
            self.url_1 = url[1]
        self.captcha = type_of_captcha

    async def send(self):
        if self.url_1:
            print(self.url_1)
            print(self.url)
            response = requests.get(self.url)
            ee = base64.b64encode(response.content)

            response_1 = requests.get(self.url_1)
            ee_1 = base64.b64encode(response_1.content)

            payload = {'textinstructions': self.captcha, 'click': 'geetest', 'key': self.key, 'method': 'base64',
                       'body0': ee, "body1": ee_1}
        else:
            print(self.url_1)
            response = requests.get(self.url)
            ee = base64.b64encode(response.content)

            payload = {'textinstructions': self.captcha, 'click': 'geetest', 'key': self.key, 'method': 'base64',
                       'body': ee}

        r = requests.post("http://api.cap.guru/in.php", data=payload)
        print("wait")
        await asyncio.sleep(10)
        rt = r.text.split('|')
        url = 'http://api.cap.guru/res.php?key=' + self.key + '&id=' + rt[1]

        response = requests.get(url).text
        if not response:
            while response == '':
                await asyncio.sleep(10)
                rt = r.text.split('|')
                url = 'http://api.cap.guru/res.php?key=' + self.key + '&id=' + rt[1]
                response = requests.get(url).text

        print(response)
        return response


if __name__ == "__main__":
    C = Cap([
        "https://p16-rc-captcha-useast2a.tiktokcdn-eu.com/tos-useast2a-i-447w7jt563-euttp/a166216c69fe437cb0a45e0d29da0b11~tplv-447w7jt563-2.jpeg",
        "https://p19-rc-captcha-useast2a.tiktokcdn-eu.com/tos-useast2a-i-447w7jt563-euttp/73ff3232923643b48eb04b21b782a599~tplv-447w7jt563-2.jpeg"],
            'koleso')
    asyncio.run(C.send())
