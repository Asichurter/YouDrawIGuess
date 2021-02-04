import logging


class Logger(object):
    """
    终端打印不同颜色的日志，在pycharm中如果强行规定了日志的颜色， 这个方法不会起作用， 但是
    对于终端，这个方法是可以打印不同颜色的日志的。
    """

    # 在这里定义StreamHandler，可以实现单例， 所有的logger()共用一个StreamHandler
    ch = logging.StreamHandler()

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(5)
        # if not self.logger.handlers:
        #     # 如果self.logger没有handler， 就执行以下代码添加handler
        #     self.logger.setLevel(logging.DEBUG)
        #     from serviceProgram.utils.FileUtil import FileUtil
        #     rootPath = FileUtil.getProgrameRootPath()
        #     self.log_path = rootPath + '/logs'
        #     if not os.path.exists(self.log_path):
        #         os.makedirs(self.log_path)
        #
        #     # 创建一个handler,用于写入日志文件
        #     fh = logging.FileHandler(self.log_path + '/runlog' + time.strftime("%Y%m%d", time.localtime()) + '.log',
        #                              encoding='utf-8')
        #     fh.setLevel(logging.INFO)
        #
        #     # 定义handler的输出格式
        #     formatter = logging.Formatter('[%(asctime)s] - [%(levelname)s] - %(message)s')
        #     fh.setFormatter(formatter)
        #
        #     # 给logger添加handler
        #     self.logger.addHandler(fh)

    def debug(self, module, message):
        self.font_color('\033[0;34m%s\033[0m', module)
        self.logger.debug(message)

    def info(self, module, message):
        self.font_color('\033[0;32m%s\033[0m', module)
        self.logger.info(message)

    def warning(self, module, message):
        self.font_color('\033[0;33m%s\033[0m', module)
        self.logger.warning(message)

    def error(self, module, message):
        self.font_color('\033[0;31m%s\033[0m', module)
        self.logger.error(message)

    def critical(self, module, message):
        self.font_color('\033[0;35m%s\033[0m', module)
        self.logger.critical(message)

    def font_color(self, color, module):
        # 不同的日志输出不同的颜色
        formatter = logging.Formatter(color % f'%(asctime)s - %(levelname)s - [{module}] %(message)s')
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)


if __name__ == "__main__":
    logger = Logger()
    logger.info(1, "12345")
    logger.debug(1, "12345")
    logger.warning(1, "12345")
    logger.error(1, "12345")
    logger.critical(1, '1234')