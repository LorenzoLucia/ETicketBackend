import uuid

from firebase_admin import firestore
from flask import abort

def get_zone(db, zone_id):
    return db.collection('zones').document(zone_id).get().to_dict()


def get_all_zones(db):
    result = db.collection('zones').get()
    return [i.to_dict() for i in result]


def add_new_zone(db, name: str, hour_price: float):
    uuid4 = str(uuid.uuid4())
    db.collection('zones').document(uuid4).set({
        "name": name,
        "hour_price": hour_price
    })

    return db.collection('zones').document(uuid4).get()


def delete_zone(db, zone_id: str):
    db.collection("zones").document(zone_id).delete()

