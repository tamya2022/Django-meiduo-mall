from django.conf import settings
from django.core.files.storage import Storage

# 自定义文件存储系统
class FastDFSStorage(Storage):
    def __init__(self, fsdf_base_url=None):
        self.fsdf_base_url = fsdf_base_url or settings.FDFS_BASE_URL

    # 4. 必须实现 _open _save
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    # 5. url 拼接全路径
    def url(self, name):
        return self.fsdf_base_url + name
