import socket
import argparse
import sys

BUFFER_SIZE = 65535

# Create args parser
parser = argparse.ArgumentParser(description="")
parser.add_argument("--port", required=True, type=int, help="Host port")

# Parse args
args = parser.parse_args()
port = args.port

addr = ("", port)

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(addr)

# Receive packets
while True:
    try:
        msg, address = s.recvfrom(BUFFER_SIZE)
    except KeyboardInterrupt:
        print("Keyboard interrupted.")
        s.close()
        sys.exit(0)
