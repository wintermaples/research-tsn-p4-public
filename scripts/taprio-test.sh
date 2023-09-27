#!/bin/bash

tc qdisc replace dev eth0 parent root \
handle 100 taprio \
num_tc 3 \
map 2 2 1 0 2 2 2 2 2 2 2 2 2 2 2 2 \
queues 1@0 1@0 1@0 \
base-time 0 \
sched-entry S 01 300000 \
sched-entry S 02 300000 \
sched-entry S 04 10000 \
flags 0x1 \
txtime-delay 40000 \
clockid CLOCK_TAI

tc qdisc replace dev eth1 parent 100:1 etf \
skip_sock_check \
delta 200000 clockid CLOCK_TAI

tc qdisc replace dev eth1 parent 100:2 etf \
skip_sock_check \
delta 200000 clockid CLOCK_TAI

iperf3 -c iperf-server -t 10
