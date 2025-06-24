import uuid

from services.payment_methods import get_payment_method
from services.plates import get_plate
from services.zones import get_zone


def get_user_tickets(db, user_id: str):
    user_tickets = db.collection('tickets').where("user", "==", user_id).get()
    tickets = []
    for i in user_tickets:
        zone = get_zone(db, i["zone_id"])
        plate = get_plate(db, i["plate_id"])
        payment_method = get_payment_method(db, i["payment_method_id"])
        tickets.append({
            "zone": zone,
            "plate": plate,
            "user_id": i["user_id"],
            "payment_method": payment_method,
            "start_time": i["start_time"],
            "end_time": i["end_time"],
            "price": i["price"],
        })
    return tickets


def add_ticket(db, user_id: str, plate_id: str, zone_id: str, payment_method_id: str, start_time, end_time,
               price: float):
    uuid4 = str(uuid.uuid4())
    ticket_ref = db.collection("tickets").document(uuid4)
    ticket_ref.set({
        "user_id": user_id,
        "plate_id": plate_id,
        "zone_id": zone_id,
        "payment_method_id": payment_method_id,
        "start_time": start_time,
        "end_time": end_time,
        "price": price
    })
    return ticket_ref.get().to_dict()
