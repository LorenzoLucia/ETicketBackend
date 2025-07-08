import uuid
from flask import abort


def get_all_chalks(db, cnt_id: str):
    result = db.collection('chalk').where('cnt_id', '==', cnt_id).get()

    return [i.to_dict()['plate'] for i in result]


def chalk(db, cnt_id: str, plate: str):
    if (db.collection('chalk').where('cnt_id', '==', cnt_id).where('plate', '==', plate).get()):
        return abort(400, "Chalk already exists for this plate and cnt_id")
    
    uuid4 = str(uuid.uuid4())
    db.collection('chalk').document(uuid4).set({
        "cnt_id": cnt_id,
        "plate": plate
    })

    return db.collection('chalk').document(uuid4).get().to_dict()


def remove_chalk(db, cnt_id: str, plate: str):
    chalk_ref = db.collection('chalk').where('cnt_id', '==', cnt_id).where('plate', '==', plate).get()
    if not chalk_ref:
        return abort(404, "Chalk not found for this plate and cnt_id")
    
    chalk_id = chalk_ref[0].id
    db.collection('chalk').document(chalk_id).delete()

    return {"message": "Chalk removed successfully"}
