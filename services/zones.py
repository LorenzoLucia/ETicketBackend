import uuid

from firebase_admin import firestore
from flask import abort

def get_zone(db, zone_id):
    return db.collection('zones').document(zone_id).get().to_dict()


def get_all_zones(db):
    result = db.collection('zones').get()
    results_ids = [i.id for i in result]
    for i in range(len(result)):
        result[i] = result[i].to_dict()
        result[i]['id'] = results_ids[i]
    return result


def add_new_zone(db, name: str, hour_price: float):
    existing_zones = db.collection('zones').where("name", "==", name).get()
    for zone in existing_zones:
        db.collection('zones').document(zone.id).delete()
    uuid4 = str(uuid.uuid4())
    db.collection('zones').document(uuid4).set({
        "name": name,
        "price": f"{hour_price:.2f}"
    })

    return db.collection('zones').document(uuid4).get().to_dict()


def delete_zone(db, zone_id: str):
    db.collection("zones").document(zone_id).delete()
    return True

