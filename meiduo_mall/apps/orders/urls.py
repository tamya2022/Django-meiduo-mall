from django.conf.urls import url
from . import views

urlpatterns = [
    # 结算订单
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    # 2. orders/commit/ 提交订单
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='commit'),

    # 3. 订单成功 -- orders/success/
    url(r'^orders/success/$', views.OrderSuccessView.as_view(), name='sucess'),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view(), name='info'),
]
