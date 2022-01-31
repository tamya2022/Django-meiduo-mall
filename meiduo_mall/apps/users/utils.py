import re
import logging
from django.contrib.auth.backends import ModelBackend
from apps.users.models import User

logger = logging.getLogger('django')


class UsernameMobileAuthBackend(ModelBackend):
    # 重写父类的认证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1.获取校验完毕的 user
        user = get_user_by_account(username)
        # 2. 校验密码 ,如果通过返回user对象
        if user and user.check_password(password):
            return user


def get_user_by_account(account):
    try:
        # 如果是手机号  验证码手机号
        if re.match(r'^1[345789]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            # 不是手机号  验证username
            user = User.objects.get(username=account)
    except User.DoesNotExist as e:
        logger.error(e)
        return None
    else:
        return user
