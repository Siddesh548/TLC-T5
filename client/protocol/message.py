import json
from enum import Enum

class MessageType(Enum):
    HANDSHAKE = 1
    HANDSHAKE_ACK = 2
    HEARTBEAT = 3
    COMMAND = 4
    RESPONSE = 5
    DISCONNECT = 6
    ERROR = 7
    ACK = 8  # Explicit acknowledgment

class Message:
    def __init__(self, msg_type: MessageType, seq=0, payload=None):
        self.msg_type = msg_type
        self.seq = seq
        self.payload = payload or {}

    def serialize(self):
        msg_dict = {
            'type': self.msg_type.value,
            'seq': self.seq,
            'payload': self.payload
        }
        return json.dumps(msg_dict).encode('utf-8')

    @staticmethod
    def deserialize(data):
        try:
            msg_dict = json.loads(data.decode('utf-8'))
            return Message(
                msg_type=MessageType(msg_dict['type']),
                seq=msg_dict['seq'],
                payload=msg_dict['payload']
            )
        except Exception:
            return Message(MessageType.ERROR, payload={'error': 'Corrupted message'})