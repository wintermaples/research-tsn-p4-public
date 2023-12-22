#!/bin/bash

ethtool -K enp2s0 gso off
ethtool -K enp2s0 gro off
ethtool -K enp2s0 tso off

ethtool -s enp2s0 speed 100

# pkill -f phc2sys
# phc2sys -s /dev/ptp0 -c CLOCK_REALTIME -O 0 &

DEV=enp2s0

sudo ip link add link $DEV name $DEV.0 type vlan id 1 egress-qos-map 0:0 1:1 2:2 3:3 4:4 5:5 6:6 7:7
sudo ip addr add 192.168.25.3/24 dev $DEV.0
sudo ip link set $DEV.0 up

tc qdisc del dev $DEV root

tc qdisc replace dev $DEV parent root \
handle 1 stab overhead 24 taprio \
num_tc 2 \
map 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 \
queues 1@0 1@0 \
base-time 0 \
sched-entry S 03 986880 \
flags 0x1 \
txtime-delay 200000 \
clockid CLOCK_TAI

tc qdisc replace dev $DEV parent 1:1 handle 10 etf \
skip_sock_check \
delta 1000000 clockid CLOCK_TAI

tc -s qdisc show dev $DEV
