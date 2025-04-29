import uuid

from common.enums import PaymentType


class PaymentMethod:

    def __init__(self, type: PaymentType, user_id: str, code: str):
        self.id = str(uuid.uuid4())
        self.type = type
        self.user_id = user_id
        self.code = code

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "user_id": self.user_id,
            "code": self.code
        }
