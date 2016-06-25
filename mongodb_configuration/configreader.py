# -*- coding: utf-8 -*-
__author__ = 'xu'

import ConfigParser
import logging
import os

logger = logging.getLogger('Main.ConfigReader')


class ConfigReader(object):
    def __init__(self):
        self.cp = ConfigParser.ConfigParser()

    def init(self, cf=None):
        try:
            if not os.path.exists(cf):
                print 'Error: specified config file does not exist.'
                raise IOError, "specified config file does not exist"
            else:
                logger.log(logging.INFO, 'Use %s. [%s]' % (cf, self.__class__.__name__))
                self.cp.read(cf)
        except IOError, e:
            logger.error('%s [%s]' % (e.message, self.__class__.__name__))
            return False
        else:
            return True

    # 读取配置参数
    def read_config(self, section, option, t=None):
        try:
            if t == 'int':
                return self.cp.getint(section, option)
            elif t == 'float':
                return self.cp.getfloat(section, option)
            elif t == 'bool':
                return self.cp.getboolean(section, option)
            else:
                return self.cp.get(section, option)
        except ConfigParser.Error or ValueError, e:
            logger.error('%s [%s]' % (e.message, self.__class__.__name__))
            return None

    def exist_option(self, section, option):
        return self.cp.has_option(section, option)