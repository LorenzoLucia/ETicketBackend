from firebase_admin import firestore, auth
from flask import abort
from google.cloud.firestore_v1 import FieldFilter
from datetime import datetime, timezone

from common.enums import Role
from models.user import User
from pytz import timezone



def get_all_users(db):
    users = db.collection('users').get()
    users_dicts = [i.to_dict() for i in users]
    users_ids = [i.id for i in users]
    for i in range(len(users_dicts)):
        users_dicts[i]['id'] = users_ids[i]
    return users_dicts


def delete_user(db, user_id: str):
    user_to_delete_ref = db.collection("users").document(user_id)
    user_to_delete = user_to_delete_ref.get().to_dict()
    # You cannot delete via APIs SYSTEM and SERVICE ADMINISTRATORS
    if user_to_delete["role"] == Role.SYSTEM_ADMINISTRATOR.value or user_to_delete[
        "role"] == Role.CUSTOMER_ADMINISTRATOR.value:
        abort(401)

    user_to_delete_ref.delete()


def register_new_user(db, name, surname, email, birth_date=datetime.now(timezone('Europe/Rome')), role=Role.CUSTOMER):
    user = User(name=name, surname=surname, email=email, role=role, birth_date=birth_date)
    db.collection("users").document(user.id).set(user.to_dict())
    return user.to_dict()


def get_myself(db, email: str):
    result = db.collection("users").where(filter=FieldFilter("email", "==", email)).get()

    if len(result) == 0:
        return {
            "is_registered": False,
            "user_data": {}
        }
    return {"is_registered": True, "user_data": result[0].to_dict(), "user_id": result[0].id}
