from django.conf.urls import url

from . import views

urlpatterns = [
    # 1.获取图形验证码  image_codes/(?P<uuid>[\w-]+)/
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view(), name='img_code'),

    # 2. 短信验证码sms_codes/(?P<mobile>1[3-9]\d{9})/
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view(), name='sms_code'),
]
