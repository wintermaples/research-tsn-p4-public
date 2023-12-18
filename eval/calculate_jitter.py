from itertools import groupby
from typing import Any
from scapy.all import sniff, rdpcap, Packet
from scapy.layers.inet import UDP
import math
import logging
from decimal import Decimal
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
import statistics

pcap_file_folder_path = '/home/yoshida/Documents/research-tsn-p4/experiment/'

@dataclass
class Statistics:
    is_taprio_enabled: bool
    rate_mb_of_load_traffic: float
    avg_delay_us: float
    max_delay_us: float
    jitter_us: float
    num_loss: int

    def __str__(self) -> str:
        return f"Taprio: {self.is_taprio_enabled}, RateOfLoadTraffic: {self.rate_mb_of_load_traffic}mb/s, MaxDelay: {self.max_delay_us}us, Jitter: {self.jitter_us}us Loss: {self.num_loss}pkt"

def calculate_jitter(delays: list[float]):
    delays_diff_sum = 0
    for i in range(1, len(delays)):
        delays_diff_sum += abs(delays[i] - delays[i-1])
    return delays_diff_sum / (len(delays) - 1)

def analyze_pcapng_file(pcapng_file_path: Path) -> Statistics:
    file_name_splited_underscore = pcapng_file_path.stem.split('_')
    is_taprio_enabled = file_name_splited_underscore[0] == 'true'
    rate_mb_of_load_traffic = float(file_name_splited_underscore[1])

    with pcapng_file_path.open('rb') as pcapng_file:
        packets: list[Packet] = rdpcap(pcapng_file) # type: ignore

    packets_grouped_by_payload = {}
    for packet in packets:
        key = packet[UDP].payload.load.hex()
        val = packets_grouped_by_payload.get(key, [])
        if val is None:
            val = []
        val.append(packet)
        packets_grouped_by_payload[key] = val

    delays = []
    num_loss = 0
    for payload, packets in packets_grouped_by_payload.items():
        if len(packets) != 2:
            num_loss += 1
            continue
        delays.append((Decimal(packets[1].time) - Decimal(packets[0].time)).copy_abs())

    avg_delay_us = statistics.mean(delays) * (10**6)
    max_delay_us = max(delays) * (10**6)
    jitter_us = calculate_jitter(delays) * (10**6)

    return Statistics(
        is_taprio_enabled=is_taprio_enabled,
        rate_mb_of_load_traffic=rate_mb_of_load_traffic,
        avg_delay_us=avg_delay_us,
        max_delay_us=max_delay_us,
        jitter_us=jitter_us,
        num_loss=num_loss,
    )
    

def main():
    pcapng_statistics_list: list[Statistics] = []
    for pcapng_file_path in Path(pcap_file_folder_path).glob('*.pcapng'):
        pcapng_statistics_list.append(
            analyze_pcapng_file(pcapng_file_path)
        )

    pcapng_statistics_list = sorted(pcapng_statistics_list, key=lambda x:x.rate_mb_of_load_traffic)
    [ print(f"{x.is_taprio_enabled},{x.rate_mb_of_load_traffic},{x.avg_delay_us},{x.max_delay_us},{x.jitter_us},{x.num_loss}") for x in pcapng_statistics_list ]


if __name__ == '__main__':
    main()
