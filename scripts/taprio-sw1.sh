#!/bin/bash

ethtool -K enp1s0 gso off
ethtool -K enp1s0 gro off
ethtool -K enp1s0 tso off
ethtool -K enp3s0 gso off
ethtool -K enp3s0 gro off
ethtool -K enp3s0 tso off

pkill -f phc2sys
phc2sys -s /dev/ptp0 -c CLOCK_REALTIME -O 0 &

tc qdisc del dev enp1s0 root

tc qdisc replace dev enp1s0 parent root \
handle 100 taprio \
num_tc 3 \
map 2 2 1 0 2 2 2 2 2 2 2 2 2 2 2 2 \
queues 1@0 1@0 1@0 \
base-time 0 \
sched-entry S 01 900000 \
sched-entry S 02 900000 \
sched-entry S 04 300000 \
flags 0x1 \
txtime-delay 40000 \
clockid CLOCK_TAI

tc qdisc replace dev enp1s0 parent 100:1 etf \
skip_sock_check \
offload delta 200000 clockid CLOCK_TAI

tc qdisc replace dev enp1s0 parent 100:2 etf \
skip_sock_check \
offload delta 200000 clockid CLOCK_TAI
