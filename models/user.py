import uuid

from common.enums import Role


class User:
    def __init__(self, username: str, email: str, password: str, role: Role):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            "password": self.password,
            'role': self.role.name
        }
