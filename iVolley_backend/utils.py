from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


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
