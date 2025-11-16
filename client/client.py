import os
import socket
import time
from protocol.protocol import ProtocolHandler
from protocol.message import MessageType, Message

HOST = os.getenv('SERVER_HOST', '127.0.0.1')
PORT = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

protocol = ProtocolHandler(sock, name='client')
protocol.handshake_client(client_id='client1')
protocol.start_heartbeat()

max_messages = 5 
RUN_DURATION = 60  
start_time = time.time() # stop after sending 5 commands
count = 0

while protocol.connected and count < max_messages:
    msg = Message(MessageType.COMMAND, payload={'command': 'ping'})
    
    # Start timer before sending
    start_time = time.time()
    protocol.send_message(msg)

    # Wait for server response
    response = None
    while True:
        response = protocol.receive_message()
        if response and response.msg_type == MessageType.RESPONSE:
            break

    # End timer after receiving response
    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000  # convert to milliseconds
    print(f"[{count+1}] Round-trip latency: {latency_ms:.2f} ms")

    count += 1
    time.sleep(10)  # interval between commands

# After sending all commands, disconnect automatically
protocol.disconnect()
print("Client finished sending messages and disconnected.")
