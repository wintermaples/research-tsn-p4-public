import socket
import argparse
from datetime import datetime, timedelta
import time
from struct import pack

SO_TXTIME = 61

def s_to_ns(seconds: int):
    """
    Convert seconds to nano seconds.
    """
    return seconds * (10 ** 9)

# Create args parser
parser = argparse.ArgumentParser(description="")
parser.add_argument("--prio", type=int, default=0, help="Socket priority (SO_PRIORITY)")
parser.add_argument("--host", required=True, type=str, help="Host address")
parser.add_argument("--port", required=True, type=int, help="Host port")
parser.add_argument("--payload-size", required=True, type=int, help="Payload size")
parser.add_argument("--time", required=True, type=int, help="Communication time in seconds")
parser.add_argument("--interval", required=True, type=int, help="Communication interval in nanoseconds")

# Parse args
args = parser.parse_args()
addr = (args.host, args.port)
prio = args.prio
payload_size_bytes = args.payload_size
time_s = args.time
interval_ns = args.interval

# Create payload
payload = bytes([0] * payload_size_bytes)

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, prio)
s.setsockopt(socket.SOL_SOCKET, SO_TXTIME, pack('iI', 11, 1))

# Send packets until end time
start_clock_tai = time.clock_gettime_ns(time.CLOCK_TAI)
end_clock_tai = start_clock_tai + s_to_ns(time_s)
n = 0
while True:
    # Calc tx time
    tx_time = start_clock_tai + n * interval_ns
    n += 1

    # If tx_time > end_clock_tai, break
    if tx_time > end_clock_tai:
        break

    # Send packet
    s.sendmsg(
        [payload],
        [
            (
                socket.SOL_SOCKET,
                SO_TXTIME,
                (tx_time).to_bytes(8, 'big')
            )
        ],
        0,
        addr,
    )
