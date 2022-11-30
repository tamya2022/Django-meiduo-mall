import logging


def log():
    """
    日志等级 level debug info waning error 严重
    :return:
    """
    logger = logging.getLogger('django')
    logger.info('测试配置的日志能否记录信息!')


if __name__ == '__main__':
    log()
