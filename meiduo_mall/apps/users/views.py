import json
import re
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django import http
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
# Create your views here.
from apps.users import constants
from apps.users.models import User
from django.contrib.auth import authenticate, login, logout

from utils.response_code import RETCODE

logger = logging.getLogger('django')


class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        data = json.loads(request.body.decode())
        email = data.get('email')

        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 赋值email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        from apps.users.utils import generate_verify_email_url
        verify_url = generate_verify_email_url(request.user)
        # print(verify_url)
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)
        # 响应添加邮箱结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 用户中心
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


class LogoutView(View):
    def get(self, request):
        """
        退出
        :param request:
        :return:
        """
        # 清空session
        logout(request)

        # 清空cookie
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')
        return response


class LoginView(View):
    def get(self, request):
        """
        登录
        :param request:
        :return:
        """
        return render(request, 'login.html')

    def post(self, request):
        # 1.接收三个参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2.校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('参数不齐全')

        # 2.1 用户名
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 2.2 密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        # 认证登录用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 实现状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户：浏览器会话结束就过期
            request.session.set_expiry(0)
        else:
            # 记住用户：None表示两周后过期
            request.session.set_expiry(None)

        # response = redirect(reverse('contents:index'))
        # 接收next的值==路由
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            # 6.返回响应结果
            response = redirect(reverse('contents:index'))
        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # 响应登录结果
        return response


class RegisterView(View):
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
        response.set_cookie('username', username, constants.USERNAME_EXPIRE_TIME)

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
