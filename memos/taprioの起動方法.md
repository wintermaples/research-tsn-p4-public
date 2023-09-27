# Taprioの起動方法

## 注意点
Dockerの環境でしか動作しない。

Vagrant(Virtualbox)ではtaprioを実行しようとすると```Operation not supported```で怒られる。

## 起動方法
以下のスクリプトを実行する。

```bash
#!/bin/bash

tc qdisc del dev eth0 root

tc qdisc replace dev eth0 parent root \
handle 100 taprio \
num_tc 3 \
map 2 2 1 0 2 2 2 2 2 2 2 2 2 2 2 2 \
queues 1@0 1@0 1@0 \
base-time 0 \
sched-entry S 01 30000 \
sched-entry S 02 90000 \
sched-entry S 04 180000 \
flags 0x1 \
txtime-delay 40000 \
clockid CLOCK_TAI

tc qdisc replace dev eth0 parent 100:1 etf \
skip_sock_check \
delta 800000 clockid CLOCK_TAI

tc qdisc replace dev eth0 parent 100:2 etf \
skip_sock_check \
delta 800000 clockid CLOCK_TAI
```

eth0ポートに対して、

- SO_PRIORITY=2: Traffic Class 1
- SO_PRIORITY=3: Traffic Class 0
- SO_PRIORITY=0, 1, 4, ..., 15: Traffic Class 2

として設定している。

## Taprioが効いているかの検証
priority指定ができるiperfでpriorityを設定して、priorityごとに通信速度が変わることを測定する。
