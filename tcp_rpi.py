import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 10000
server_address = ('192.168.0.220', PORT)
print(f'starting up {server_address}')
sock.bind(server_address)

sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()

    try:
        print(f'connection from {client_address}')

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(64)
            print(f'received {data}')
            if data:
                pass
            else:
                print(f'no more data from {client_address}')
                break

    finally:
        # Clean up the connection
        connection.close()