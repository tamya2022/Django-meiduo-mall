import logging

from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contents.utils import get_categories
from apps.contents.models import ContentCategory

logger = logging.getLogger('django')


class IndexView(View):
    def get(self, request):
        """提供首页广告界面"""
        # 查询商品频道和分类
        categories = get_categories()

        # 广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        # print(content_categories)
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)
