import uuid
from datetime import datetime, timedelta

import pytz
from google.cloud.firestore_v1 import FieldFilter

from services.payment_methods import get_payment_method
from services.plates import get_plate
from services.zones import get_zone


def get_user_tickets(db, user_id: str):
    user_tickets = db.collection('tickets').where(filter=FieldFilter("user_id", "==", user_id)).get()
    tickets = []
    for i in user_tickets:
        id = i.id
        i = i.to_dict()
        zone = get_zone(db, i["zone_id"])
        plate = get_plate(db, i["plate_id"])
        payment_method = get_payment_method(db, i["payment_method_id"])

        current_time = datetime.now(pytz.timezone("Europe/Rome"))
        if (current_time - timedelta(days=30)) > i["end_time"]: continue

        is_active = i["end_time"] > current_time
        # print(is_active)
        tickets.append({
            "zone": zone,
            "plate": plate,
            "user_id": i["user_id"],
            "payment_method": payment_method,
            "start_time": i["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": i["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "price": i["price"],
            'id': id,
            'is_active': is_active
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
        "price": str(price)
    })
    return ticket_ref.get().to_dict()


def extend_ticket(db, ticket_id: str, duration: int, amount: float):
    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket = ticket_ref.get().to_dict()

    if not ticket:
        return None

    new_end_time = ticket["end_time"] + timedelta(minutes=duration * 30)

    ticket_ref.update({
        "end_time": new_end_time,
        "price": str(float(ticket["price"]) + float(amount))
    })

    return ticket_ref.get().to_dict()
