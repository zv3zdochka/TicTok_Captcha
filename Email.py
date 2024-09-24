import imaplib
import email
from email.header import decode_header


class TikTokEmailFetcher:
    def __init__(self, email_account, password):
        self.email_account = email_account
        self.password = password

    def fetch_last_tiktok_code(self):
        # Подключение к почтовому ящику
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            mail.login(self.email_account, self.password)
            mail.select('inbox')

            # Поиск всех писем от TikTok
            result, data = mail.uid('search', None, '(FROM "noreply@account.tiktok.com")')
            if result == 'OK':
                email_uids = data[0].split()
                if not email_uids:
                    print("Нет писем от TikTok.")
                    return None

                email_uids.reverse()  # Самые новые письма идут в начале

                for email_uid in email_uids:
                    result, email_data = mail.uid('fetch', email_uid, '(RFC822)')
                    if result == 'OK':
                        raw_email = email_data[0][1]
                        email_message = email.message_from_bytes(raw_email)

                        # Получаем тему письма
                        subject, encoding = decode_header(email_message['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or 'utf-8')
                            code = subject.split()[0]
                            if len(code) == 6 and code.isdigit():
                                print(code)
                                return code

                print("Код не найден в письмах TikTok.")
            else:
                print("Не удалось получить письма.")
        finally:
            mail.logout()

if __name__ == "__main__":
    # Пример использования
    email_account = "incognitiincognito126@gmail.com"
    password = "tuyq bkhc ukcw cpum"

    fetcher = TikTokEmailFetcher(email_account, password)
    fetcher.fetch_last_tiktok_code()
