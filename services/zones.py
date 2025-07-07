import uuid


def get_zone(db, zone_id):
    return db.collection('zones').document(zone_id).get().to_dict()


def get_all_zones(db):
    result = db.collection('zones').get()
    results_ids = [i.id for i in result]
    zones_to_return = []
    for i in range(len(result)):
        zone_dict = result[i].to_dict()

        if zone_dict['show']:
            zone_dict['id'] = results_ids[i]
            zones_to_return.append(zone_dict)

    return zones_to_return


def add_new_zone(db, name: str, hour_price: float):
    existing_zones = db.collection('zones').where("name", "==", name).get()
    for zone in existing_zones:
        db.collection('zones').document(zone.id).delete()
    uuid4 = str(uuid.uuid4())
    db.collection('zones').document(uuid4).set({
        "name": name,
        "price": f"{hour_price:.2f}",
        "show": True
    })

    return db.collection('zones').document(uuid4).get().to_dict()


def delete_zone(db, zone_id: str):
    zone = db.collection('zones').document(zone_id).get().to_dict()
    zone["show"] = False
    db.collection("zones").document(zone_id).set(zone)
