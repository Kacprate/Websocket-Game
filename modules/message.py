from enum import Enum
import json
import modules.logger as logger

logger = logger.get_logger(__name__)

class Message:
    def __init__(self, message_type: str, data):
        super().__init__()
        self.message_type = message_type
        self.data = data

    def pack(self):
        try:
            data = json.dumps({'message_type': self.message_type, 'data': self.data})
            return data
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def from_packed(pack):
        try:
            pack = json.loads(pack)
            return Message(pack['message_type'], pack['data'])
        except Exception as e:
            logger.error(e)
            return None
        