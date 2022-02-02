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
]
