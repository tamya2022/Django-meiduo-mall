import logging

from celery_tasks.main import app
from libs.yuntongxun.sms import CCP

logger = logging.getLogger('django')


@app.task(bind=True, name="send_sms_code", retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    #   手机号   验证码 过期时间 1短信模板
    try:
        send_ret = CCP().send_template_sms(mobile, [sms_code, 5], 1)

    except Exception as e:
        logger.error(e)
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)

    if send_ret != 0:
        # 有异常自动重试三次
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)

    print(f"celery验证码:{sms_code}")
    return send_ret
