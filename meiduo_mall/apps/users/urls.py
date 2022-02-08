from django.conf.urls import url
from . import views

urlpatterns = [
    # 注册页面
    url(r'^register/$', views.RegisterView.as_view(), name="register"),
    # 判断用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view(), name="count"),
    # 登录页面
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    # 退出
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view(), name="info"),
    # 增加邮箱
    url(r'^emails/$', views.EmailView.as_view(), name="email"),
    # 8. 激活邮箱 emails/verification/
    url(r'^emails/verification/$', views.VerifyEmailView.as_view(), name="verify_email"),
    # 9.收货地址  address/
    url(r'^address/$', views.AddressView.as_view(), name="address"),
    # 10. 新增地址 addresses/create/
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name="create_address"),
    # 11. 修改地址 addresses/(?P<address_id>\d+)/
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateAddressView.as_view(), name="update_address"),
    # # 12 .addresses/(?P<address_id>\d+)/default/
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name="default_address"),
    # # 13 . 修改标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(), name="title_address"),
    url(r'^password/$', views.ChangePasswordView.as_view(), name="password"),
]
