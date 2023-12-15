#!/bin/bash

ethtool -K enp1s0 gso off
ethtool -K enp1s0 gro off
ethtool -K enp1s0 tso off
ethtool -K enp3s0 gso off
ethtool -K enp3s0 gro off
ethtool -K enp3s0 tso off
ethtool -K enx3495db2e4350 gso off
ethtool -K enx3495db2e4350 gro off
ethtool -K enx3495db2e4350 tso off

ethtool -s enp1s0 speed 10
ethtool -s enp3s0 speed 10
ethtool -s enx3495db2e4350 speed 10

# pkill -f phc2sys
# phc2sys -s /dev/ptp0 -c CLOCK_REALTIME -O 0 &

##### enp1s0 #####
DEV="enp1s0"

tc qdisc del dev $DEV root
tc qdisc del dev $DEV clsact

tc qdisc replace dev $DEV parent root \
handle 1: taprio \
num_tc 2 \
map 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 \
queues 1@0 1@1 \
base-time 0 \
sched-entry S 01 4934400 \
sched-entry S 02 1233600 \
flags 0x2

tc qdisc add dev $DEV clsact
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0x0000)" action skbedit priority 0
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0x2000)" action skbedit priority 1
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0x4000)" action skbedit priority 2
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0x6000)" action skbedit priority 3
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0x8000)" action skbedit priority 4
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0xa000)" action skbedit priority 5
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0xc000)" action skbedit priority 6
tc filter add dev $DEV egress prio 1 basic match "meta(vlan mask 0xe000 eq 0xe000)" action skbedit priority 7

tc -s qdisc show dev $DEV
tc -s filter show dev $DEV
