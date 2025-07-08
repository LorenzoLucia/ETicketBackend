import uuid
from datetime import datetime

def emit_fine(db, plate: str, cnt_id: str, reason: str, amount: float, timestamp: datetime):
    fine_id = str(uuid.uuid4())

    fine_data = {
        "plate": plate,
        "cnt_id": cnt_id,
        "reason": reason,
        "amount": amount,
        "timestamp": timestamp,
        "issued": False,
    }

    fine_ref = db.collection("fines").document(fine_id)
    fine_ref.set(fine_data)

    return 'True'

def issue_fine(db, fine_id: str):
    fine_ref = db.collection("fines").document(fine_id)
    
    fine_ref.update({"issued": True})
    
    return fine_ref.id

def get_fines(db):
    fines = db.collection("fines").get()
    return [{
        "id": fine.id,
        "amount": fine.to_dict()["amount"],
        "plate": fine.to_dict()["plate"],
        "reason": fine.to_dict()["reason"],
        "timestamp": fine.to_dict()["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
        "issued": fine.to_dict()["issued"],
    } for fine in fines]
