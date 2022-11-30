from django.conf.urls import url
from . import views

urlpatterns = [
    # 1. 列表页面 list/(?P<category_id>\d+)/(?P<page_num>\d+)/
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),

    # 2. 热销排行 hot/(?P<category_id>\d+)/
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view(), name='hot'),

    # 3.详情页 detail/(?P<sku_id>\d+)/
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),

    # 4.访问量 detail/visit/(?P<category_id>\d+)/
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view(), name='visit'),

]
