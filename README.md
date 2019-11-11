# Azkaban-HA-Bootstrap
A solution for azkaban web service HA

Azkaban Web Service 目前不支持高可用，这会存在单点问题，并且如果Web Service挂掉了 定时调度的任务就不再运行，这对于生产环境是灾难性的。
使用 Python + Zookeeper 实现了高可用的启动脚本，利用ZK做master选举，备节点sleep等待不占用机器性能若主节点挂掉自动接管。

使用了Python的Kazoo与ZK交互因此需要先安装
``` bash
pip install kazoo
```

日志目前直接打印到标准输出，可以配合 supervisor 使用
启动方式
```
./startup_distributed_mode.py
```
