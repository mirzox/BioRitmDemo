import requests
import json


SMS_SERVICE_EMAIL = "test@eskiz.uz"
SMS_SERVICE_PASSWORD = "j6DWtQjjpLDNjWEk74Sx"
SMS_SERVICE_LOGIN = "https://notify.eskiz.uz/api/auth/login"
SMS_SEND_URL = "https://notify.eskiz.uz/api/message/sms/send"
SMS_STATUS_URL = "https://notify.eskiz.uz/api/message/sms/status/{}/"
SMS_LIMIT_URL = "https://notify.eskiz.uz/api/user/get-limit/"
FROM = "4546"


class SmsService:
    def __init__(self):
        self.login_url = SMS_SERVICE_LOGIN
        self.sms_url = SMS_SEND_URL
        self.email = SMS_SERVICE_EMAIL
        self.password = SMS_SERVICE_PASSWORD
        self.sms_status_check_url = SMS_STATUS_URL
        self.sms_limit_url = SMS_LIMIT_URL
        self.from_ = FROM
        self.token = json.loads(self.open_json('token.json'))
        self.headers = {'Authorization': 'Bearer {}'.format(self.token['token']),
                        'User-Agent': 'Mozilla/5.0'}

    def open_json(self, filename):
        with open(filename, encoding='utf-8') as f:
            return f.read()

    def save(self, token: str) -> None:
        _json = json.dumps({'token': token})
        with open("token.json", "w") as f:
            f.write(_json)

    def login(self) -> None:
        data = {"email": self.email, "password": self.password}
        request = requests.post(url=self.login_url, data=data)
        if request.status_code == 200:
            self.save(request.json()['data']['token'])

    def check_status(self, sms_id: int):
        request = requests.get(url=self.sms_status_check_url.format(str(sms_id)),  headers=self.headers)
        if request.status_code == 200:
            return request.json()
        else:
            self.login()
            return requests.get(url=self.sms_status_check_url.format(str(sms_id)), headers=self.headers).json()

    def get_limit(self):
        request = requests.get(url=self.sms_limit_url, headers=self.headers)
        if request.status_code == 200:
            return request.json()
        else:
            self.login()
            return requests.get(url=self.sms_limit_url, headers=self.headers).json()

    def send_sms(self, phone: str, message: str):
        payload = {
            'mobile_phone': phone,
            'message': message,
            'from': self.from_
        }
        request = requests.post(url=self.sms_url, headers=self.headers, data=payload)
        if request.status_code == 200:
            return request.json()
        else:
            self.login()
            return requests.post(url=self.sms_url, headers=self.headers, data=payload).json()


# import time
# from random import randint
# from django.core.cache import cache


# Sms.login()
# Sms.send_sms('998972746839', "awd165ad")
# for i in range(10):
#     print(Sms.send_sms('998972746839', 'Тестовое сообщение'))
#     time.sleep(10)
# def func():
#     code = randint(1000, 9999)
#     phone = '998972746839'
#     cache.set(f"{phone}", code, timeout=20)
#     print(Sms.send_sms(phone, f'Ваш код подтвержения номера {code}'))
#     time.sleep(15)
#     cache.set(f"{phone}", code, timeout=20)
#     print(cache.get(phone))
#     time.sleep(15)
#     print(cache.get(phone))


# class SendSms(APIView):
#     def id_generator(self, size=15, chars=string.ascii_lowercase + string.digits):
#         return ''.join(random.choice(chars) for _ in range(size))
#
#     def post(self, request):
#         user = get_object_or_404(User, username=request.data.get('username'), email=request.data.get('email'))
#         otp = OneTimeUrl.objects.create(user_id=user, code=self.id_generator(), phone=request.data.get('phone'))
#         url = "notify.eskiz.uz/api/message/sms/send"
#         payload = {'mobile_phone': '998991234567',
#                    'message': f'Ваша ссылка http://127.0.0.1:8000/api/resetpassword{otp.code}/',
#                    'from': '4546'}
#
#         headers = {
#             'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9ub3RpZnkuZXNraXoudXpcL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE2NDE4MzI3NzEsImV4cCI6MTY0NDQyNDc3MSwibmJmIjoxNjQxODMyNzcxLCJqdGkiOiI1V3RSZ0hhbko5MGh6NlM3Iiwic3ViIjo1LCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.fENou5x9p5jFQQvtt2KapOFDTIEEHqC00Mtb5cmkUMQ'
#         }
#         response = requests.request("POST", url, headers=headers, data=payload)
#         return Response({})