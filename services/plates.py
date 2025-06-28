import uuid

from flask import abort


def get_plate(db, plate_id: str):
    return db.collection('plates').document(plate_id).get().to_dict()


def get_user_plates(db, user_id: str):
    user_plates = db.collection('plates').where("user", "==", user_id).get()
    print([i.to_dict() for i in user_plates])
    return [i.to_dict() for i in user_plates]


def add_user_plate(db, user_id: str, number: str):
    uuid4 = str(uuid.uuid4())
    db.collection('plates').document(uuid4).set({
        "user_id": user_id,
        "number": number})

    return db.collection('plates').document(uuid4).get()


def delete_plate(db, user_id: str, plate_id: str):
    plate_ref = db.collection('plates').document(plate_id)
    plate = plate_ref.get().to_dict()
    if plate["user_id"] != user_id:
        return abort(401)

    plate_ref.delete()
