# Qdisc to filter packets
tc qdisc add dev enp42s0 root handle 1: prio bands 2 priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

# Filter vlan packets and set priority based on vlan PCP
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0x0000)" \
flowid 10: \
action skbedit priority 0
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0x2000)" \
flowid 10: \
action skbedit priority 1
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0x4000)" \
flowid 10: \
action skbedit priority 2
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0x6000)" \
flowid 10: \
action skbedit priority 3
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0x8000)" \
flowid 10: \
action skbedit priority 4
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0xa000)" \
flowid 10: \
action skbedit priority 5
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0xc000)" \
flowid 10: \
action skbedit priority 6
tc filter add dev enp42s0 protocol ip parent 1: prio 0 \
basic match "meta(vlan mask 0x8000 eq 0xe000)" \
flowid 10: \
action skbedit priority 7

# TODO: Taprio
tc qdisc add dev enp42s0 parent 1:1 handle 10: prio bands 3 priomap 0 1 2 2 2 2 2 2 2 2 2 2 2 2 2 2
