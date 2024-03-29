#!/bin/bash

ethtool -K enp1s0 gso off
ethtool -K enp1s0 gro off
ethtool -K enp1s0 tso off
ethtool -K enp3s0 gso off
ethtool -K enp3s0 gro off
ethtool -K enp3s0 tso off

ethtool -s enp1s0 speed 100
ethtool -s enp3s0 speed 100

pkill -f phc2sys
phc2sys -s /dev/ptp0 -c CLOCK_REALTIME -O 0 &


##### enp1s0 #####
tc qdisc del dev enp1s0 root

tc qdisc replace dev enp1s0 parent root \
handle 100 taprio \
num_tc 3 \
map 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 \
queues 1@0 1@0 1@0 \
base-time 0 \
sched-entry S 01 246720 \
sched-entry S 02 493440 \
sched-entry S 04 123360 \
flags 0x1 \
txtime-delay 200000 \
clockid CLOCK_TAI

tc qdisc replace dev enp1s0 parent 100:1 etf \
skip_sock_check \
delta 100000 clockid CLOCK_TAI

# tc qdisc replace dev enp1s0 parent 100:2 etf \
# skip_sock_check \
# offload delta 100000 clockid CLOCK_TAI

##### enp3s0
tc qdisc del dev enp3s0 root

tc qdisc replace dev enp3s0 parent root \
handle 101 taprio \
num_tc 3 \
map 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 \
queues 1@0 1@0 1@0 \
base-time 0 \
sched-entry S 01 246720 \
sched-entry S 02 493440 \
sched-entry S 04 123360 \
flags 0x1 \
txtime-delay 200000 \
clockid CLOCK_TAI

tc qdisc replace dev enp3s0 parent 101:1 etf \
skip_sock_check \
delta 100000 clockid CLOCK_TAI

# tc qdisc replace dev enp3s0 parent 101:2 etf \
# skip_sock_check \
# offload delta 100000 clockid CLOCK_TAI
