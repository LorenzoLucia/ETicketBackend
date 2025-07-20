import uuid

from google.cloud.firestore_v1 import FieldFilter
from flask import abort


def get_plate(db, plate_id: str):
    return db.collection('plates').document(plate_id).get().to_dict()


def get_user_plates(db, user_id: str):
    user_plates = db.collection('plates').where(filter=FieldFilter("user_id", "==", user_id)).where(
        filter=FieldFilter("show", "==", True)).get()

    return [i.to_dict()['number'] for i in user_plates]


def add_user_plate(db, user_id: str, number: str):
    if len(db.collection('plates').where(filter=FieldFilter("number", "==", number)).where(
            filter=FieldFilter("user_id", "==", user_id)).get()) > 0:
        return abort(400, "Plate already exists")
    uuid4 = str(uuid.uuid4())
    db.collection('plates').document(uuid4).set({
        "user_id": user_id,
        "number": number,
        "show": True})

    return db.collection('plates').document(uuid4).get().to_dict()


def delete_plate(db, user_id: str, number: str):
    plate_id = db.collection('plates').where(filter=FieldFilter("number", "==", number)).where(
        filter=FieldFilter("user_id", "==", user_id)).get()[0].id
    plate_ref = db.collection('plates').document(plate_id)
    plate_data = plate_ref.get().to_dict()
    plate_data["show"] = False
    plate_ref.set(plate_data)
