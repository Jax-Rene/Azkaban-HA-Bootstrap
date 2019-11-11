#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from kazoo.client import KazooClient
from kazoo.client import NodeExistsError
import logging
import time
import socket
import sys
import os

""" 参数定义 """
zk_host = "put your zk path"
zk_path = "/azkaban"
path = '%s/node' % zk_path  # 临时节点路径
azkaban_node = 'node'
hostname = socket.gethostname()
azkaban_web_home = '/usr/local/azkaban-web-server-3.53.0'


def startup_azkaban(event=None):
    """ 启动azkaban """
    zk.create(path, value=hostname, ephemeral=True)
    logging.info("create node successfully, election to leader, trying to startup azkaban")
    cmd = 'cd %s && %s' % (azkaban_web_home, os.path.join(
        azkaban_web_home, 'bin', 'internal', 'internal-start-web.sh'))
    logging.info("execute cmd:%s" % cmd)
    os.system(cmd)


if __name__ == "__main__":
    """
        Azkaban Web Service 分布式模式启动脚本，
        使用Zookeeper,保证同一时刻只有一个服务在运行，另外一个服务保持Watching热备,
        1. 启动前先检测是否已经开启了Web Service，若是则尝试Kill
        2. 若机器宕机或者服务宕掉，备服务自动接管，并主服务恢复后作为备等待运行
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("starting azkaban, zookeeper address: %s ... " % zk_host)
    zk = KazooClient(hosts=zk_host)
    zk.start()

    try:
        # 若父节点不存在则创建
        if not zk.exists(zk_path):
            logging.info('zk path %s not exist creating it now.' % zk_path)
            zk.create(zk_path, 'azkaban')
        try:
            startup_azkaban()
        except NodeExistsError as e:
            logging.info("node existing. current master:%s" % (zk.get(path)[0]))
            zk.get_children(path, watch=startup_azkaban)
            # keep watching
            time.sleep(3153600000)
        except Exception as e:
            raise(e)
    except Exception as e:
        logging.exception(e)
    finally:
        zk.stop()
