from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
import random


def get_account(user_email):
    try:
        user = User.objects.get(username__exact=user_email)
    except User.DoesNotExist as e:
        return None
    return user


class AuthPasswordUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_account(user_id=username)
        if user and user.check_password(password):
            return user
        return None


def generate_random_str(randomlength=8):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghigkmnopqrstuvwxyz123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str

