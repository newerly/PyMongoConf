__author__ = 'root'

import os
import sys
import time
import logging
from termcolor import cprint

from configreader import ConfigReader
from deployment import Deployment

__doc__ = "=============================================================\n" \
          "Allowed options:\n" \
          "start/stop [shard/shardpro/initreplset/addreplshard/configsvr/mongos]\n\n" \
          "NOTE:\n" \
          "1) Setup order:\n" \
          "2) In shardpro mode, initialize the replset only once whether distributed or standalone\n" \
          "\n" \
          "Example:\n" \
          "python mongodb.py start [configsvr]\n\n" \
          "If there is any trouble, please check the log and make sure the configuration is correct.\n" \
          "================================================================="


def config_logger(log_file, log_level):
    # logger configuration
    logger = logging.getLogger('Main')
    LEVELS = {
        1: logging.CRITICAL,
        2: logging.ERROR,
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG
    }
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    try:
        file_hdr = logging.FileHandler(log_file)
    except IOError, e:
        cprint('%s Error: %s' % (time.ctime(), e.message), 'red', attrs=['bold'])
        return False
    else:
        file_hdr.setFormatter(formatter)
        logger.addHandler(file_hdr)
        logger.setLevel(LEVELS.get(log_level))
        return True


def main(ops):
    if ops[0] == 'start':
        if not config_logger('logs.log', 4):
            cprint('%s Error occurs when create logging handler.' % time.ctime(),
                   'red', attrs=['bold'])
            return
        conf_reader = ConfigReader()
        if not conf_reader.init('conf.cfg'):
            cprint('%s Error occurs when initialize the config reader.' % time.ctime(),
                   'red', attrs=['bold'])
            return
        # launch mongodb in specified working state
        logging.getLogger('Main').log(logging.INFO, '%s [%s]' % ('Launching MongoDB...', 'Main'))
        t = conf_reader.read_config('deployment', 'type')
        try:
            deployment = Deployment(conf_reader, t)
            if t == 'standalone':
                deployment.launch(None)
            elif t == 'sharding':
                if ops[1] not in ['shard', 'replset', 'configsvr', 'mongos', 'initreplset',
                                  'addshard', 'addreplshard']:
                    raise NotImplementedError('Not implemente this operation: %s' % ops[1])
                deployment.launch(ops[1])
        except Exception, e:
            cprint('%s Error: %s' % (time.ctime(), e.message), 'red', attrs=['bold'])
            return 1
    elif ops[0] == 'stop':
        os.system('killall -v mongod')
        os.system('killall -v mongos')

if __name__ == '__main__':
    argc = len(sys.argv)
    #main(['start', 'addreplshard'])
    if argc < 2:
        print __doc__
        exit(1)
    if os.geteuid() != 0:
        cprint('%s Error: Need to be root' % time.ctime(), 'red', attrs=['bold'])
        exit(1)
    if sys.argv[1] in ['start', 'stop']:
        main(sys.argv[1:])
    elif sys.argv[1] == 'help':
        print __doc__
    else:
        cprint('%s Error: No such operation, see help: python mongodb.py help' % time.ctime(),
               'red', attrs=['bold'])