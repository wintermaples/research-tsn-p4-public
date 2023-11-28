from itertools import groupby
from typing import Any
from scapy.all import sniff, rdpcap, Packet
from scapy.layers.inet import UDP
import math
import logging
from decimal import Decimal

pcap_file_folder_path = '/home/yoshida/Documents/research-tsn-p4/experiment/'
pcap_file_name = 'test.pcapng'
pcap_file_path = pcap_file_folder_path + pcap_file_name

def calculate_jitter(delays: list[float]):
    delays_diff_sum = 0
    for i in range(1, len(delays)):
        delays_diff_sum += delays[i] - delays[i-1]
    return delays_diff_sum / (len(delays) - 1)

packets: list[Packet] = rdpcap(pcap_file_path)

packets_grouped_by_payload = {}
for packet in packets:
    key = packet[UDP].payload.load[0:8].hex()
    val = packets_grouped_by_payload.get(key, [])
    if val is None:
        val = []
    val.append(packet)
    packets_grouped_by_payload[key] = val

delays = []
for payload, packets in packets_grouped_by_payload.items():
    if len(packets) != 2:
        logging.warn(f"Packets pair that number is not 2! It will ignore.")
        continue
    delays.append((Decimal(packets[1].time) - Decimal(packets[0].time)).copy_abs())

max_delay = max(delays)
jitter = calculate_jitter(delays)

print(f"Max Delay: {max_delay}s")
print(f"Jitter: {jitter}s")
