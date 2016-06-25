__author__ = 'root'

import os
import time
import logging
from termcolor import cprint


logger = logging.getLogger('Main.Deployment')


class Deployment(object):
    def __init__(self, cr, t):
        self.conf_reader = None
        self.t = None
        self.dbinfo = None
        self.deployment = None
        if t == 'standalone':
            from standalone import Standalone
            self.deployment = Standalone(cr, t)
        elif t == 'sharding':
            from sharding import Sharding
            self.deployment = Sharding(cr, t)
        else:
            raise NotImplementedError('Not implement this configuration type: %s' % t)

    def launch(self, op):
        self.deployment.start(op)

    def start(self, op):
        pass

    def existconfigs(self, configlist):
        # check the necessary configurations
        for item in configlist:
            if not self.conf_reader.exist_option(self.t, item):
                logger.error("miss '%s' [%s]" % (item, self.__class__.__name__))
                cprint("%s Miss %s, returned" % (time.ctime(), item), 'red', attrs=['bold'])
                raise KeyError('Miss %s in configuration' % item)
            if item.endswith('dbpath'):
                path = self.conf_reader.read_config(self.t, item)
                if path.endswith('/'):
                    path = path[:-1]
                self.dbinfo[item] = path
            elif item.endswith('dirpath'):
                path = self.conf_reader.read_config(self.t, item)
                if not path.endswith('/'):
                    path = ''.join([path, '/'])
                self.dbinfo[item] = path
            else:
                self.dbinfo[item] = self.conf_reader.read_config(self.t, item)

    def existpath(self, pathlist, paths=None, type=None):
        def mkdir(_path):
            if not os.path.exists(_path):
                logger.info('make dir %s [%s]' % (item, self.__class__.__name__))
                print '%s make dir %s' % (time.ctime(), _path)
                os.system('mkdir -p %s' % _path)
        # make sure the existing db and log path
        if pathlist:
            for item in pathlist:
                if item in self.dbinfo:
                    if item in ['configdbpath', 'sharddbpath', 'replsetdbpath'] and \
                                    self.dbinfo[item.replace('dbpath', 'type')] == 'standalone':
                        for i in xrange(1, int(self.dbinfo['confignum'])+1):
                            path = ''.join([self.dbinfo[item], str(i)])
                            mkdir(path)
                    else:
                        path = self.dbinfo[item]
                        mkdir(path)
        if paths:
            path = '/'.join([self.dbinfo[item] for item in paths])
            if self.dbinfo[type] == 'standalone':
                map(lambda i: mkdir('%s%d' % (path, i)), xrange(1, int(self.dbinfo[type.replace('type', 'num')])+1))
            else:
                mkdir(path)