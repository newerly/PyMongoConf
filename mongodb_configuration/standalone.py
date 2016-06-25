__author__ = 'root'

from termcolor import cprint
import logging
import time
import os

from deployment import Deployment

logger = logging.getLogger('Main.Standalone')


class Standalone(Deployment):
    def __init__(self, cr, t):
        self.conf_reader = cr
        self.t = t
        self.dbinfo = {}

    def start(self, op):
        self.existconfigs(['port', 'dbpath'])
        # the others are optional
        for item in ['logdirpath', 'journal', 'rest']:
            if self.conf_reader.exist_option('standalone', item):
                if item in ['journal', 'rest']:
                    self.dbinfo[item] = self.conf_reader.read_config('standalone', item, 'bool')
                else:
                    self.dbinfo[item] = self.conf_reader.read_config('standalone', item)

        self.existpath(['dbpath', 'logdirpath'])

        # well, let's goooooooo
        cmd = 'mongod --port %s --dbpath %s' % \
              (self.dbinfo['port'], self.dbinfo['dbpath'])
        if 'logdirpath' in self.dbinfo:
            cmd = ''.join([cmd, ' --fork --logpath %s%s.log' % (self.dbinfo['logdirpath'], time.strftime('%Y%m%d%H%M%S'))])
        if 'journal' in self.dbinfo and self.dbinfo['journal']:
            cmd = ''.join([cmd, ' --journal'])
        if 'rest' in self.dbinfo and self.dbinfo['rest']:
            cmd = ''.join([cmd, ' --rest'])
        cprint('>> %s' % cmd, 'cyan')
        os.system(cmd)