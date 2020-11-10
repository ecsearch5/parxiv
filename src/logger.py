import logging
import os


class Logger(logging.Logger):
    def __init__(self, name=None,
                 to_file=True,
                 to_dir=None,
                 level=logging.DEBUG,
                 *args, **kwargs):
        super(Logger, self).__init__(name=name, level=level, *args, **kwargs)
        self.to_file = to_file
        self.to_dir = to_dir

    def addHandler(self, hdlr=None):
        super(Logger, self).addHandler(hdlr)

    def addFilter(self, filt=None):
        super(Logger, self).addFilter(filt)

    def debug(self, msg, *args, **kwargs):
        super(Logger, self).debug(msg=msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        super(Logger, self).info(msg=msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        super(Logger, self).warn(msg=msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Fatal error following by an exit
        """
        super(Logger, self).error(msg=msg, *args, **kwargs)
        exit(1)


class ClassicLogger(Logger):
    def __init__(self, *args, **kwargs):
        super(ClassicLogger, self).__init__(*args, **kwargs)
        self.formatter = logging.Formatter(fmt="[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s-L%(lineno)d]: %(message)s")
        # When logging to files
        if self.to_file and self.name is not None \
                and self.to_dir is not None:
            self.filename = os.path.join(self.to_dir, self.name + ".log")
            if not os.path.exists(self.to_dir):
                os.makedirs(self.to_dir)
            self.initHandlers()

    def initHandlers(self):
        handler = logging.FileHandler(self.filename, encoding="UTF-8")
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        self.addHandler(handler)

