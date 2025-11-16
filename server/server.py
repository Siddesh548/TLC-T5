from protocol.protocol import ProtocolHandler
from protocol.message import MessageType, Message

import socket
from protocol.protocol import ProtocolHandler
from protocol.message import MessageType
from threading import Thread

HOST = '0.0.0.0'
PORT = 9000

def handle_client(client_sock, addr):
    protocol = ProtocolHandler(client_sock, name=f'server-{addr}')
    protocol.handshake_server()
    protocol.start_heartbeat()
    try:
        while protocol.connected:
            msg = protocol.receive_message()
            if msg is None:
                break
            if msg.msg_type == MessageType.COMMAND:
                protocol.handle_command(msg)
            elif msg.msg_type == MessageType.DISCONNECT:
                protocol.disconnect()
            elif msg.msg_type == MessageType.ERROR:
                print(f"Received error from client: {msg.payload}")
    except KeyboardInterrupt:
        protocol.disconnect()

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((HOST, PORT))
server_sock.listen(5)
print("Server listening on port", PORT)

while True:
    client_sock, addr = server_sock.accept()
    Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()
