class Broker(object):
    """任务队列"""
    broker_list = []


class Worker(object):
    """任务执行者"""

    def run(self, broker, func):
        """
        执行任务
        :param broker: 任务队列
        :param func: 任务
        """
        # 如果任务在任务队列中，就取出来执行
        if func in broker.broker_list:
            # 执行任务
            func()
        else:
            return 'error'


class Celery(object):
    """Celery内部简单构造演示"""

    def __init__(self):
        """初始化Celery对象"""

        # 创建任务队列
        self.broker = Broker()
        # 创建任务执行者
        self.worker = Worker()

    def add(self, func):
        """
        将任务添加到任务队列
        :param func: 任务
        """
        self.broker.broker_list.append(func)

    def work(self, func):
        """
        任务执行者执行任务
        :param func: 任务
        """
        self.worker.run(self.broker, func)


def send_sms_code():
    """要执行的任务"""
    print('send_sms_code')


if __name__ == '__main__':
    # 创建Celery实例
    app = Celery()
    # 向Celery中添加任务
    app.add(send_sms_code)
    # Celery执行任务
    app.work(send_sms_code)
