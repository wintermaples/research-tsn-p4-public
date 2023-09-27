import socket
import time

client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
    0
)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, 4)

addr = ('172.23.0.2', 8000)

client_socket.connect(addr)

print(f'Connected to {addr}')

send_time = 10
send_rate = 1

while True:
    print(f'Sending rate is {send_rate} characters/s')
    for i in range(send_time * send_rate):
        client_socket.send(b'.')
        time.sleep(1 / send_rate)
    client_socket.send(b'\n\n\n')
    send_rate *= 2
    