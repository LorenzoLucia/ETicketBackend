import uuid
from datetime import datetime


class Ticket:

    def __init__(self, price: float, plate: str, expiration_date: datetime, start_date: datetime, user_id: str):
        self.id = str(uuid.uuid4())
        self.price = price
        self.plate = plate
        self.expiration_date = expiration_date
        self.start_date = start_date
        self.user_id = user_id
        self.fine = None

    def fine_ticket(self, fine):
        self.fine = fine

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'plate': self.plate,
            'expiration_date': self.expiration_date,
            'start_date': self.start_date,
            'user_id': self.user_id,
            'fine': self.fine
        }
