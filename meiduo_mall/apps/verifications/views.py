import logging
import random
import json

from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from celery_tasks.sms.tasks import send_sms_code

from apps.verifications import constants
from libs.captcha.captcha import captcha

# 创建日志输出器
from utils.response_code import RETCODE

logger = logging.getLogger('django')


# Create your views here.
# 1.获取图片验证码 GET
class ImageCodeView(View):
    def get(self, request, uuid):
        # 1.生成图片验证码
        text, image_code = captcha.generate_captcha()

        # 2.想redis缓存 存 验证码text
        image_redis_client = get_redis_connection('verify_image_code')
        image_redis_client.setex("img_%s" % uuid, constants.IMAGE_CODE_EXPIRE_TIME, text)

        # 3.返回图片验证码 image_code
        return http.HttpResponse(image_code, content_type='image/jpeg')


class SMSCodeView(View):
    def get(self, request, mobile):
        # 接收图片验证码
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 校验参数
        if not all([image_code, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            img_redis_client = get_redis_connection('verify_image_code')
            redis_img_code = img_redis_client.get("img_%s" % uuid)

            if not redis_img_code:
                return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码过期!'})

            # 千万注意: redis返回的是 bytes 不能直接对比 bytes.decode()
            if redis_img_code.decode().lower() != image_code.lower():
                return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码错误!'})
            # 删除以前的图片验证码
            img_redis_client.delete("img_%s" % uuid)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code': RETCODE.DBERR,
                'errmsg': 'redis异常'
            })
        # 频繁发送短信验证码
        sms_redis_client = get_redis_connection('sms_code')
        # 取出 redis 保存发短信标识
        send_flag = sms_redis_client.get('send_flag_%s' % mobile)
        if send_flag:
            ret = {'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'}
            return http.HttpResponse(json.dumps(ret, ensure_ascii=False), content_type="application/json,charset=utf-8")

        # 生成短信验证码 6位 随机码
        sms_code = '%06d' % random.randint(0, 999999)
        # redis存储 短信验证码
        try:
            p1 = sms_redis_client.pipeline()
            p1.setex('send_flag_%s' % mobile, constants.SMSCODE_SEND_TIME, 1)
            p1.setex('sms_%s' % mobile, constants.SMSCODE_EXPIRE_TIME, sms_code)
            p1.execute()
        except Exception as e:
            logger.error(e)

        # 容联云发送短信---celery异步发送
        send_sms_code.delay(mobile, sms_code)

        # 发送短信完毕--让前端 倒计时 60秒
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'}, json_dumps_params={'ensure_ascii': False})
