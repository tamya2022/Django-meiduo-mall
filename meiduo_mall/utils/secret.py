from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer


class SecretOauth(object):
    def __init__(self):
        self.serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=3600 * 10)

    # 1.加密
    def dumps(self, data):
        result = self.serializer.dumps(data)
        return result.decode()

    # 2.解密
    def loads(self, data):
        result = self.serializer.loads(data)
        return result
