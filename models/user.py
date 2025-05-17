import uuid

from common.enums import Role


class User:
    def __init__(self, name: str, surname: str, email: str, role: Role):
        self.id = str(uuid.uuid4())
        self.name = name
        self.surname = surname
        self.email = email
        self.role = role


    def to_dict(self):
        return {
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'role': self.role.name,
        }
