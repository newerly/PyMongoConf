__author__ = 'root'

from termcolor import cprint
import logging
import time
import os

from deployment import Deployment

logger = logging.getLogger('Main.Sharding')


class Sharding(Deployment):
    def __init__(self, cr, t):
        self.conf_reader = cr
        self.t = t
        self.dbinfo = {}

    def start(self, op):
        if op == 'shard':
            self.existconfigs(['shardtype', 'sharddbpath', 'shardlogdirpath', 'shardport', 'confignum'])
            self.existpath(['sharddbpath', 'shardlogdirpath'])
            self.__start_shard()
        elif op == 'replset':
            self.existconfigs(['replsettype', 'replsetdbpath', 'replsetlogdirpath', 'replsetport', 'replsetnum', 'replsetname', 'oplogsize'])
            self.existpath(['replsetlogdirpath'], paths=['replsetdbpath', 'replsetname'], type='replsettype')
            self.__start_replset()
        elif op == 'configsvr':
            self.existconfigs(['configtype', 'confignum', 'configdbpath', 'configport', 'configlogdirpath'])
            self.existpath(['configdbpath', 'configlogdirpath'])
            self.__start_config_server()
        elif op == 'mongos':
            self.existconfigs(['configtype', 'configdbs', 'mongosport', 'mongoslogdirpath', 'chunksize', 'confignum', 'configport'])
            self.existpath(['mongoslogdirpath'])
            self.__start_mongos()
        elif op == 'initreplset':
            self.existconfigs(['replsethost', 'replsettype', 'replsetport', 'replsetnum', 'replsetname'])
            self.__init_replset()
        elif op == 'addreplshard':
            self.existconfigs(['mongosport', 'configdbs', 'replsethost', 'replsettype', 'replsetport', 'replsetnum', 'replsetname'])
            self.__addreplshard()

    def __start_shard(self):
        def mkcmd(_cmd, counter):
            if counter:
                _cmd = ''.join([_cmd, '--dbpath %s%d --port %d --logpath %sshard%d_%s.log --fork --rest' %
                                      (self.dbinfo['sharddbpath'],
                                       counter,
                                      int(self.dbinfo['shardport'])+counter,
                                      self.dbinfo['shardlogdirpath'],
                                      counter,
                                      time.strftime('%Y%m%d%H%M%S'))])
            else:
                _cmd = ''.join([_cmd, '--dbpath %s --port %s --logpath %s%s.log --fork --rest' %
                                      (self.dbinfo['sharddbpath'],
                                      self.dbinfo['shardport'],
                                      self.dbinfo['shardlogdirpath'],
                                      time.strftime('%Y%m%d%H%M%S'))])
            return _cmd
        if self.dbinfo['shardtype'] == 'distributed':
            cmd = mkcmd('mongod ', None)
            cprint('>> %s' % cmd, 'cyan')
            os.system(cmd)
        elif self.dbinfo['shardtype'] == 'standalone':
            for i in xrange(1, int(self.dbinfo['confignum'])+1):
                cmd = mkcmd('mongod ', i)
                cprint('>> %s' % cmd, 'cyan')
                os.system(cmd)

    def __start_replset(self):
        def mkcmd(_cmd, counter):
            if counter:
                _cmd = ''.join([_cmd, '--dbpath %s/%s%d --port %d --logpath %sreplset%d_%s.log --fork '
                                      '--replSet %s --oplogSize %s --rest' %
                                      (self.dbinfo['replsetdbpath'],
                                       self.dbinfo['replsetname'],
                                       counter,
                                      int(self.dbinfo['replsetport'])+counter,
                                      self.dbinfo['replsetlogdirpath'],
                                      counter,
                                      time.strftime('%Y%m%d%H%M%S'),
                                      self.dbinfo['replsetname'],
                                      self.dbinfo['oplogsize'])])
            else:
                _cmd = ''.join([_cmd, '--dbpath %s/%s --port %s --logpath %s%s.log --fork '
                                      '--replSet %s --oplogSize %s --rest' %
                                      (self.dbinfo['replsetdbpath'],
                                       self.dbinfo['replsetname'],
                                      self.dbinfo['replsetport'],
                                      self.dbinfo['replsetlogdirpath'],
                                      time.strftime('%Y%m%d%H%M%S'),
                                      self.dbinfo['replsetname'],
                                      self.dbinfo['oplogsize'])])
            return _cmd
        if self.dbinfo['replsettype'] == 'distributed':
            cmd = mkcmd('mongod ', None)
            cprint('>> %s' % cmd, 'cyan')
            os.system(cmd)
        elif self.dbinfo['replsettype'] == 'standalone':
            for i in xrange(1, int(self.dbinfo['replsetnum'])+1):
                cmd = mkcmd('mongod ', i)
                cprint('>> %s' % cmd, 'cyan')
                os.system(cmd)

    def __start_config_server(self):
        def mkcmd(_cmd, counter):
            if counter:
                _cmd = ''.join([_cmd, ' --dbpath %s%d --port %d --logpath %sconfig%d_%s.log --fork' %
                                      (self.dbinfo['configdbpath'],
                                       counter,
                                       int(self.dbinfo['configport']) + counter,
                                       self.dbinfo['configlogdirpath'],
                                       counter,
                                       time.strftime('%Y%m%d%H%M%S'))])
            else:
                _cmd = ''.join([_cmd, ' --dbpath %s --port %s --logpath %s%s.log --fork' %
                                      (self.dbinfo['configdbpath'],
                                       self.dbinfo['configport'],
                                       self.dbinfo['configlogdirpath'],
                                       time.strftime('%Y%m%d%H%M%S'))])
            return _cmd
        if self.dbinfo['configtype'] == 'distributed':
            cmd = mkcmd('mongod --configsvr', None)
            cprint('>> %s' % cmd, 'cyan')
            os.system(cmd)
        elif self.dbinfo['configtype'] == 'standalone':
            for i in xrange(1, int(self.dbinfo['confignum'])+1):
                cmd = mkcmd('mongod --configsvr', i)
                cprint('>> %s' % cmd, 'cyan')
                os.system(cmd)

    def __start_mongos(self):
        if self.dbinfo['configtype'] == 'distributed':
            configdbs = self.dbinfo['configdbs'].split(',')
            cmd = 'mongos --logpath %s%s.log --fork --port %s --chunkSize %s --configdb ' % \
                  (self.dbinfo['mongoslogdirpath'],
                  time.strftime('%Y%m%d%H%M%S'),
                  self.dbinfo['mongosport'],
                  self.dbinfo['chunksize'])
            for db in configdbs:
                cmd = ''.join([cmd, '%s:%s,' % (db, self.dbinfo['configport'])])
            cprint('>> %s' % cmd[:-1], 'cyan')
            os.system(cmd[:-1])
        elif self.dbinfo['configtype'] == 'standalone':
            cmd = 'mongos --logpath %s%s.log --fork --port %s --chunkSize %s --configdb ' % \
                  (self.dbinfo['mongoslogdirpath'],
                   time.strftime('%Y%m%d%H%M%S'),
                  self.dbinfo['mongosport'],
                  self.dbinfo['chunksize'])
            for i in xrange(1, int(self.dbinfo['confignum'])+1):
                cmd = ''.join([cmd, '%s:%d,' % (self.dbinfo['configdbs'], int(self.dbinfo['configport'])+i)])
            cprint('>> %s' % cmd[:-1], 'cyan')
            os.system(cmd[:-1])

    def __init_replset(self):
        def mkmembers():
            _doc = []
            if self.dbinfo['replsettype'] == 'standalone':
                for counter in xrange(1, int(self.dbinfo['replsetnum'])+1):
                    _doc.append({"_id": counter,
                                 "host": '%s:%d' %
                                         (self.dbinfo['replsethost'], int(self.dbinfo['replsetport'])+counter)})
            elif self.dbinfo['replsettype'] == 'distributed':
                for counter, host in enumerate(self.dbinfo['replsethost'].split(',')):
                    _doc.append({"_id": counter,
                                 "host": '%s:%s' %
                                         (host, self.dbinfo['replsetport'])})
            return str(_doc)

        jsdoc = "db.runCommand({'replSetInitiate': " \
                "{'_id': '%s', 'members': %s}})" % \
                (self.dbinfo['replsetname'], mkmembers())
        f = open('replset.js', 'w')
        f.write(jsdoc)
        f.flush()
        f.close()
        cmd = ''
        if self.dbinfo['replsettype'] == 'standalone':
            cmd = 'mongo %s:%d/admin replset.js' % \
                  (self.dbinfo['replsethost'], int(self.dbinfo['replsetport'])+1)
        elif self.dbinfo['replsettype'] == 'distributed':
            cmd = 'mongo %s:%s/admin replset.js' % \
                  (self.dbinfo['replsethost'].split(',')[0], self.dbinfo['replsetport'])
        cprint('>> %s' % cmd, 'cyan')
        os.system(cmd)

    def __addreplshard(self):
        def mkshard():
            __shards = ''
            if self.dbinfo['replsettype'] == 'standalone':
                for counter in xrange(1, int(self.dbinfo['replsetnum'])+1):
                    __shards = '%s%s:%d,' % (__shards, self.dbinfo['replsethost'], int(self.dbinfo['replsetport'])+counter)
            elif self.dbinfo['replsettype'] == 'distributed':
                for host in self.dbinfo['replsethost'].split(','):
                    __shards = '%s%s:%d,' % (__shards, host, self.dbinfo['replsetport'])
            return __shards[:-1]
        jsdoc = "db.runCommand({addShard: '%s/%s'})" % \
                (self.dbinfo['replsetname'], mkshard())
        f = open('addshard.js', 'w')
        f.write(jsdoc)
        f.flush()
        f.close()
        cmd = 'mongo %s:%s/admin addshard.js' %\
              (self.dbinfo['configdbs'].split(',')[0], self.dbinfo['mongosport'])
        cprint('>> %s' % cmd, 'cyan')
        os.system(cmd)