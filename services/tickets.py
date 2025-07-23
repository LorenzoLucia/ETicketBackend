import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from github import Github
from github import Auth

import pytz
from google.cloud.firestore_v1 import FieldFilter

from common.constants import TOTEM_USER_ID
from services.payment_methods import get_payment_method
from services.plates import get_plate
from services.zones import get_zone

load_dotenv()
firestore_account_path = os.getenv('FIRESTORE_ACCOUNT_PATH')


def get_plate_tickets(db, number: str):
    today = datetime.now(pytz.timezone("Europe/Rome")).date()
    tickets = sorted(
        [t for t in db.collection('tickets').get() if t.to_dict()["end_time"].date() == today],
        key=lambda t: t.to_dict()["end_time"],
        reverse=True
    )
    plate_tickets = []
    fine_issued = [t for t in db.collection('fines').where(filter=FieldFilter("plate", "==", number)).get() if
                   t.to_dict()["timestamp"].date() == today]
    for i in tickets:
        id = i.id
        i = i.to_dict()
        plate = get_plate(db, i["plate_id"])
        if plate["number"] != number or i['end_time'].date() < datetime.now(
            pytz.timezone("Europe/Rome")).date(): continue

        zone = get_zone(db, i["zone_id"])

        start_time = i["start_time"].astimezone(pytz.timezone("Europe/Rome")).strftime("%Y-%m-%d %H:%M:%S")
        end_time = i["end_time"].astimezone(pytz.timezone("Europe/Rome")).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "has_ticket": True,
            "zone": zone,
            "plate": plate,
            "start_time": start_time,
            "end_time": end_time,
            "price": i["price"],
            'id': id,
            'fine_issued': len(fine_issued) > 0,
        }
    return {
        "has_ticket": False,
        'fine_issued': len(fine_issued) > 0,
    }


def get_user_tickets(db, user_id: str):
    user_tickets = db.collection('tickets').where(filter=FieldFilter("user_id", "==", user_id)).get()
    tickets = []
    for i in user_tickets:
        id = i.id
        i = i.to_dict()
        zone = get_zone(db, i["zone_id"])
        plate = get_plate(db, i["plate_id"])
        if plate is None:
            plate = {
                "number": "N/A",
                "id": i["plate_id"]
            }
        if zone is None:
            zone = {
                "name": "N/A",
                "id": i["zone_id"]
            }
        payment_method = get_payment_method(db, i["payment_method_id"])

        current_time = datetime.now(pytz.timezone("Europe/Rome"))
        if (current_time - timedelta(days=30)) > i["end_time"]: continue

        # Offset to add because Firestore return all the dates in UTC (even if we specified the timezone when saving the document)
        timezone_offset = timedelta(hours=2)

        is_active = i["end_time"] > current_time
        # print(is_active)
        tickets.append({
            "zone": zone,
            "plate": plate,
            "user_id": i["user_id"],
            "payment_method": payment_method,
            "start_time": (i["start_time"] + timezone_offset).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (i["end_time"] + timezone_offset).strftime("%Y-%m-%d %H:%M:%S"),
            "price": i["price"],
            'id': id,
            'is_active': is_active
        })
    # print(tickets)
    return tickets


# The last input parameter "card_name" is used only when it is a ticket bought on the totem, while payment_method_id will be None
def add_ticket(db, user_id: str, plate_id: str, zone: str,  zone_id: str, payment_method_id: str, start_time, end_time,
               duration: float, price: float, card_name=None):

    new_ticket = {
        "user_id": user_id,
        "plate_id": plate_id,
        "zone_id": zone_id,
        "payment_method_id": payment_method_id,
        "start_time": start_time,
        "end_time": end_time,
        "price": str(price)
    }

    if user_id == TOTEM_USER_ID:
        new_ticket["payment_method_id"] = None
        new_ticket["payment_method"] = card_name

    uuid4 = str(uuid.uuid4())
    ticket_ref = db.collection("tickets").document(uuid4)
    ticket_ref.set(new_ticket)

    compile_ticket_svg(db, uuid4, start_time, end_time, duration, zone, price)

    return dict(ticket_ref.get().to_dict(), ticket_id=uuid4)


def extend_ticket(db, ticket_id: str, duration: float, amount: float):
    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket = ticket_ref.get().to_dict()

    if not ticket:
        return None

    new_end_time = ticket["end_time"] + timedelta(minutes=int(duration * 60))
    new_duration = float(((new_end_time - ticket["start_time"]).total_seconds())/3600)

    ticket_ref.update({
        "end_time": new_end_time,
        "price": str(float(ticket["price"]) + float(amount))
    })

    zone = get_zone(db, ticket["zone_id"])["name"]

    # print(db, ticket_id, ticket["start_time"], new_end_time, new_duration, zone, float(ticket["price"]) + float(amount))
    compile_ticket_svg(db, ticket_id, ticket["start_time"], new_end_time, new_duration, zone, float(ticket["price"]) + float(amount))

    response = ticket_ref.get().to_dict()
    response['end_time'] = response['end_time'].astimezone(pytz.timezone("Europe/Rome")).strftime("%Y-%m-%d %H:%M:%S")
    response['success'] = True

    return response

def compile_ticket_svg(db, ticket_id: str, start_time, end_time, duration, zone: str, amount):
    # print(db, ticket_id, start_time, end_time, duration, zone, amount)
    # Format all strings properly
    amount_str = f"{amount:.2f} €"

    minutes = int(duration * 60)
    hours_str = f"{int(duration):0>2}"
    minutes_str = f"{(minutes % 60):0>2}"

    duration_str = f"{hours_str}:{minutes_str} h"
    # print(duration_str)

    start_time_str = start_time.astimezone(pytz.timezone("Europe/Rome")).strftime("%d-%m-%Y %H:%M")
    end_time_str = end_time.astimezone(pytz.timezone("Europe/Rome")).strftime("%d-%m-%Y %H:%M")

    # Compile the ticket template
    dir_path = os.path.dirname(os.path.dirname(__file__))
    with open(f"{dir_path}/common/ticket_template_card.svg", "r") as f:
        template = f.read()
        
    ticket_svg = template.replace("start_time", start_time_str)
    ticket_svg = ticket_svg.replace("end_time", end_time_str)
    ticket_svg = ticket_svg.replace("duration_time", duration_str)
    ticket_svg = ticket_svg.replace("ticket_zone", zone) 
    ticket_svg = ticket_svg.replace("ticket_amount", amount_str)
    ticket_svg = ticket_svg.replace("ticket_id", ticket_id)


    access_token = os.getenv('GITHUB_ACCESS_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')
    git_branch = "main"
    git_file_svg = f"ticket_files/{ticket_id}.svg"
    # Access github and upload or create the ticket
    try:
        # Authentication
        auth = Auth.Token(access_token)
        g = Github(auth=auth)
        for repo in g.get_user().get_repos():
            if github_repo in repo.full_name:
                totem_repo = repo
        # print("success getting repo")
    except Exception as e:
        print(e)

    git_files = []
    contents = totem_repo.get_contents("ticket_files")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(totem_repo.get_contents(file_content.path))
        else:
            file = file_content
            git_files.append(str(file).replace('ContentFile(path="', '').replace('")', ''))

    # Upload to github or create new file
    if git_file_svg in git_files:
        contents = totem_repo.get_contents(git_file_svg)
        totem_repo.update_file(contents.path, "committ ticket_svg", ticket_svg, contents.sha, branch=git_branch)
    else:
        # print("file non trovato")
        totem_repo.create_file(git_file_svg, "committ ticket_svg", ticket_svg, git_branch)

    g.close()

    # Add url to ticket on database
    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_svg_url = f"https://raw.githubusercontent.com/LorenzoLucia/ETicketTotem/refs/heads/main/ticket_files/{ticket_id}.svg"
    ticket_ref.update({
        "ticket_svg_url": ticket_svg_url,
    })

    return ticket_ref.get().to_dict()