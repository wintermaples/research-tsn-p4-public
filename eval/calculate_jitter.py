from itertools import groupby
from typing import Any
from scapy.all import sniff, rdpcap, Packet

pcap_file_path = '/Users/wintermaples/Downloads/sample.pcap'

def calculate_jitter(delays: list[float]):
    delays_diff_sum = 0
    for i in range(1, len(delays)):
        jitter_sum = delays[i] - delays[i-1]
    return delays_diff_sum / (len(delays) - 1)

packets = rdpcap(pcap_file_path)
packets_grouped_by_payload = groupby(packets, key=lambda x: x.payload)

delays = []
for payload, packets_grouper in packets_grouped_by_payload:
    packets = list(packets_grouper)
    delays = abs(packets[1].time - packets[0].time)

max_delay = max(delays)
jitter = calculate_jitter(delays)
