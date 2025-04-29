import uuid


class Fine:

    def __init__(self, price: float):
        self.id = str(uuid.uuid4())
        self.price = price
        self.is_paid = False

    def pay_fine(self):
        self.is_paid = True

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'is_paid': self.is_paid,
        }
