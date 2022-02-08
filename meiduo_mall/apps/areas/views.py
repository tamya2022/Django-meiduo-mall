import logging
# Create your views here.
from django.core.cache import cache
from django.views import View
from django import http
from apps.areas.models import Area
from utils.response_code import RETCODE

logger = logging.getLogger('django')


class AreasView(View):
    """省市区数据"""

    def get(self, request):
        """提供省市区数据"""
        area_id = request.GET.get('area_id')

        if not area_id:
            # 提供省份数据
            # 1.从缓存取出 数据,如果有 不交互数据库, 没有才交互数据库
            province_list = cache.get('province_list')
            if not province_list:
                try:
                    # 查询省份数据
                    province_model_list = Area.objects.filter(parent__isnull=True)

                    # 序列化省级数据
                    province_list = []
                    for province_model in province_model_list:
                        province_list.append({'id': province_model.id, 'name': province_model.name})
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({
                            'code': RETCODE.DBERR,
                            'errmsg': '省份数据错误'
                        })
                # 2. 存入缓存
                cache.set('province_list', province_list, 10 * 60)
                # 响应省份数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 1.从缓存取出 数据,如果有 不交互数据库, 没有才交互数据库
            sub_data = cache.get('sub_' + area_id)
            if not sub_data:
                # 提供市或区数据
                try:
                    parent_model = Area.objects.get(id=area_id)  # 查询市或区的父级
                    sub_model_list = parent_model.subs.all()

                    # 序列化市或区数据
                    sub_list = []
                    for sub_model in sub_model_list:
                        sub_list.append({'id': sub_model.id, 'name': sub_model.name})

                    sub_data = {
                        'id': parent_model.id,  # 父级pk
                        'name': parent_model.name,  # 父级name
                        'subs': sub_list  # 父级的子集
                    }
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})
                # 2. 存入缓存
                cache.set('sub_' + area_id, sub_data, 10 * 60)

            # 响应市或区数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
