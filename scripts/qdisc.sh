DEV="eth0"

tc qdisc del dev $DEV root
tc qdisc del dev $DEV clsact

tc qdisc replace dev $DEV parent root \
handle 1: taprio \
num_tc 3 \
map 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 \
queues 1@0 1@1 1@2 \
base-time 0 \
sched-entry S 01 246720 \
sched-entry S 02 493440 \
sched-entry S 04 123360 \
flags 0x1 \
txtime-delay 200000 \
clockid CLOCK_TAI

tc qdisc add dev $DEV clsact
tc filter add dev $DEV egress prio 1 u32 match ip dport 443 0xffff action skbedit priority 3

tc -s qdisc show dev $DEV
tc -s filter show dev $DEV
