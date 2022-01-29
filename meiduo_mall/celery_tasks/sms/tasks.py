# 定义发短信的任务
from celery_tasks.main import app
from libs.yuntongxun.sms import CCP


@app.task
def send_sms_code(mobile, sms_code):
    #   手机号   验证码 过期时间 1短信模板
    result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    print(f"celery验证码:{sms_code}")

    return result
