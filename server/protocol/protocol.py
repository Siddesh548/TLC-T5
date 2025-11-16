import socket
import logging
import time
from threading import Thread, Event
from protocol.message import Message, MessageType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ProtocolHandler:
    def __init__(self, sock: socket.socket, name='peer'):
        self.sock = sock
        self.seq = 0
        self.connected = False
        self.name = name
        self.heartbeat_interval = 5
        self.stop_event = Event()

    def send_message(self, msg: Message):
        msg.seq = self.seq
        self.sock.sendall(msg.serialize())
        logging.info(f"[{self.name}] Sent: {msg.msg_type.name}, Seq: {msg.seq}, Payload: {msg.payload}")
        self.seq += 1

    def receive_message(self):
        try:
            data = self.sock.recv(1024)
            if not data:
                return None
            msg = Message.deserialize(data)
            logging.info(f"[{self.name}] Received: {msg.msg_type.name}, Seq: {msg.seq}, Payload: {msg.payload}")
            return msg
        except Exception as e:
            logging.error(f"[{self.name}] Receive error: {e}")
            return Message(MessageType.ERROR, payload={'error': str(e)})

    def handshake_client(self, client_id):
        msg = Message(MessageType.HANDSHAKE, payload={'client_id': client_id})
        self.send_message(msg)
        resp = self.receive_message()
        if resp and resp.msg_type == MessageType.HANDSHAKE_ACK:
            self.connected = True
            logging.info(f"[{self.name}] Handshake successful!")

    def handshake_server(self):
        msg = self.receive_message()
        if msg and msg.msg_type == MessageType.HANDSHAKE:
            ack = Message(MessageType.HANDSHAKE_ACK, payload={'server_id': 'srv1'})
            self.send_message(ack)
            self.connected = True
            logging.info(f"[{self.name}] Handshake completed with {msg.payload.get('client_id')}")

    def start_heartbeat(self):
        def hb_loop():
            while not self.stop_event.is_set() and self.connected:
                self.send_message(Message(MessageType.HEARTBEAT))
                time.sleep(self.heartbeat_interval)
        Thread(target=hb_loop, daemon=True).start()

    def handle_command(self, msg: Message):
        resp = Message(MessageType.RESPONSE, payload={'result': f"Executed {msg.payload.get('command')}"})
        self.send_message(resp)

    def disconnect(self):
        self.send_message(Message(MessageType.DISCONNECT))
        self.connected = False
        self.stop_event.set()
        self.sock.close()
        logging.info(f"[{self.name}] Disconnected gracefully")