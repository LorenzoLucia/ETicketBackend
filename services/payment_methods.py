import uuid

from firebase_admin import firestore
from flask import abort



def get_payment_method(db, payment_method_id: str):
    return db.collection('payment-methods').document(payment_method_id).get().to_dict()

def get_user_payment_methods(db, user_id: str):
    user_payment_methods = db.collection('payment-methods').where("user_id", "==", user_id).get()
    return [{"name": i.to_dict()["name"], "id": i.id} for i in user_payment_methods]


def add_payment_methods(db, user_id: str, card_number: str, cvc: str, expiry):
    uuid4 = str(uuid.uuid4())
    method_ref = db.collection("payment-methods").document(uuid4)
    method_ref.set({
        "user_id": user_id,
        "card_number": card_number,
        "cvc": cvc,
        "expiry": expiry,
        # "id": uuid4,
        "name": f"VISA ***{card_number[-4:]}-{expiry}",
    })
    return uuid4


def delete_payment_method(db, user_id: str, payment_method_id: str):
    method_ref = db.collection('payment-methods').document(payment_method_id)
    payment_method = method_ref.get().to_dict()
    if payment_method["user_id"] != user_id:
        return abort(401)

    method_ref.delete()
