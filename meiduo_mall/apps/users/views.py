import re
import logging

from django.db import DatabaseError
from django import http
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
# Create your views here.
from apps.users.models import User

logger = logging.getLogger('django')


class RegisterView(View):
    """
    用户注册
    """

    def get(self, request):
        """
        提供用户注册页面
        :param request:
        :return:
        """
        return render(request, 'register.html')

    def post(self, request):
        """

        :param request:
        :return:
        """
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        allow = data.get('allow')
        sms_code = data.get('sms_code')

        # 数据验证
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseBadRequest('参数不全')

        # 判断用户名是否符合规范，判断5-20位 数字 字母
        if not re.match(r'[0-9a-zA-Z]{5,20}', username):
            return http.HttpResponseBadRequest('用户名不合法')
        # 判断密码是否 符合规范
        if not re.match(r'[0-9a-zA-Z]{8,20}', password):
            return http.HttpResponseBadRequest('密码不合规')

        # 确认密码和密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('密码不一致')

        # 判断手机号是否符合规范
        if not re.match(r'1[3-9]\d{9}', mobile):
            return http.HttpResponseBadRequest('手机号不符合规范')

        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户同意!')

        # 校验判空, 正则, 和后台的验证码对比
        redis_code_client = get_redis_connection('sms_code')
        redis_code = redis_code_client.get('sms_%s' % mobile)

        if redis_code is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        if redis_code.decode() != sms_code:
            return render(request, 'register.html', {'sms_code_errmsg': '不正确的短信验证码'})

        # 验证数据没有问题才入库
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError as e:
            logger.error(e)
            return render(request, 'register.html', context={'error_message': '数据库异常'})
        # 保持登陆状态
        from django.contrib.auth import login
        login(request, user)

        response = redirect(reverse('contents:index'))
        # response.set_cookie('username', username, constants.USERNAME_EXPIRE_TIME)

        return response


# 2.判断用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):
        # 去数据库校验 count
        try:
            count = User.objects.filter(username=username).count()
        except DatabaseError as e:
            return http.JsonResponse({'code': '400', 'errmsg': '数据库异常'})
        # 返回响应结果
        return http.JsonResponse({
            "code": '0',
            "errmsg": "ok",
            "count": count,
        })
