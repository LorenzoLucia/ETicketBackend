import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import firestore, credentials, auth
from firebase_admin.auth import UserNotFoundError
from flask import Flask, abort, request
from flask_cors import CORS, cross_origin
from google.cloud.firestore_v1 import FieldFilter

from common.enums import Role
from services.payment_methods import get_user_payment_methods, delete_payment_method, add_payment_methods
from services.plates import get_user_plates, add_user_plate, delete_plate
from services.tickets import get_user_tickets, add_ticket, extend_ticket
from services.users import get_all_users, delete_user, register_new_user, get_myself
from services.zones import get_all_zones, add_new_zone, delete_zone
from datetime import datetime, timedelta, timezone

load_dotenv()

firestore_account_path = os.getenv('FIRESTORE_ACCOUNT_PATH')

cred = credentials.Certificate(firestore_account_path)
firestore_app = firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def get_firebase_user(token_id):
    decoded_token = auth.verify_id_token(token_id)
    user_id = decoded_token['uid']
    try:
        return auth.get_user(user_id)
    except UserNotFoundError:
        abort(401)


def get_token(headers):
    token_id = headers.get('auth')

    if token_id is None:
        abort(401)

    return token_id


# Checks that the "user_id" in the http route is owned by the firebase user with the current "token_id".
# Therefore it cannot be used when administrators are handling other users
def is_user_authenticated(user_id, token_id):
    db_user = db.collection("users").document(user_id).get().to_dict()
    firebase_user = get_firebase_user(token_id)
    return db_user["email"] == firebase_user.email


def get_db_user_from_auth(firebase_user):
    return db.collection("users").where(filter=FieldFilter("email", "==", firebase_user.email)).get()[0].to_dict()


@app.route('/users/<user_id>/payment-methods', methods=['POST'])
@cross_origin()
def add_payment_method(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    body = request.json
    return add_payment_methods(db,
                              user_id,
                              body["card_number"],
                              body["cvc"],
                              body["expiry"])


@app.route('/users/<user_id>/payment-methods', methods=['GET'])
def get_payment_methods(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)
    return get_user_payment_methods(db, user_id)


@app.route('/users/<user_id>/payment-methods/<payment_method_id>', methods=['DELETE'])
def remove_payment_method(user_id: str, payment_method_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    delete_payment_method(db, user_id, payment_method_id)
    return ''


@app.route('/users/<user_id>/tickets', methods=['GET'])
def get_tickets(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    return get_user_tickets(db, user_id)


# @app.route('/users/<user_id>/tickets', methods=['POST'])
# def add_ticket(user_id: str):
#     token_id = get_token(request.headers)
#     if not is_user_authenticated(user_id, token_id):
#         return abort(401)

#     body = request.json()
#     return add_ticket(db,
#                       user_id,
#                       body["plate_id"],
#                       body["zone_id"],
#                       body["payment_method_id"],
#                       body["start_time"],
#                       body["end_time"],
#                       body["price"])


@app.route('/users', methods=['GET'])
def get_users():
    token_id = get_token(request.headers)
    user = get_db_user_from_auth(get_firebase_user(token_id))
    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.CUSTOMER_ADMINISTRATOR.value:
        return abort(401)

    return get_all_users(db)

#
# @app.route('/users/<user_id>', methods=['PUT'])
# def edit_user(user_id: str):
#     token_id = get_token(request.headers)
#
#     user = get_db_user_from_auth(get_firebase_user(token_id))
#     user_to_edit_ref = db.collection("users").document(user_id)
#     user_to_edit = user_to_edit_ref.get().to_dict()
#     if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.CUSTOMER_ADMINISTRATOR.value:
#         return abort(401)
#     # You cannot edit via APIs SYSTEM and SERVICE ADMINISTRATORS
#     if user_to_edit["role"] == Role.SYSTEM_ADMINISTRATOR.value or user_to_edit[
#         "role"] == Role.CUSTOMER_ADMINISTRATOR.value:
#         abort(401)
#
#     body = request.json
#     user_to_edit_ref.set(body)
#     return user_to_edit_ref.get().to_dict()


@app.route('/users/<user_id>', methods=['DELETE'])
def remove_user(user_id: str):
    token_id = get_token(request.headers)

    user = get_db_user_from_auth(get_firebase_user(token_id))

    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.CUSTOMER_ADMINISTRATOR.value:
        return abort(401)

    delete_user(db, user_id)
    return True


@app.route('/users/<user_id>/plates', methods=['GET'])
def get_plates(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    return get_user_plates(db, user_id)


@app.route('/users/<user_id>/plates', methods=['POST'])
@cross_origin()
def add_plate(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    body = request.json

    return add_user_plate(db, user_id, body["plate"])


@app.route('/users/<user_id>/plates/<number>', methods=['DELETE'])
def remove_plate(user_id: str, number: str):
    token_id = get_token(request.headers)

    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    delete_plate(db, user_id, number)
    return ''


@app.route('/zones', methods=['GET'])
def get_zones():
    token_id = get_token(request.headers)
    # This line is only needed to check that the user is authenticated
    _ = get_firebase_user(token_id)
    return get_all_zones(db, )


@app.route('/zones', methods=['POST'])
@cross_origin()
def add_zone():
    token_id = get_token(request.headers)

    user = get_db_user_from_auth(get_firebase_user(token_id))
    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.CUSTOMER_ADMINISTRATOR.value:
        return abort(401)
    body = request.json

    return add_new_zone(db, body["name"], body["hour_price"])


@app.route('/zones/<zone_id>', methods=['DELETE'])
def remove_zone(zone_id: str):
    token_id = get_token(request.headers)

    user = get_db_user_from_auth(get_firebase_user(token_id))
    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.CUSTOMER_ADMINISTRATOR.value:
        return abort(401)

    delete_zone(db, zone_id)
    return True


#
# @app.route('/zones/<zone_id>', methods=['PUT'])
# def edit_zone(zone_id: int):
#     token_id = get_token(request.headers)
#
#     body = request.json
#
#     return firebase.put('/zones/edit-zone', body, params={"auth": token_id})
#
#


@app.route('/get-me', methods=['GET'])
def get_me():
    token_id = get_token(request.headers)
    firebase_user = get_firebase_user(token_id)
    email = firebase_user.email
    return get_myself(db, email)


@app.route('/register', methods=['POST'])
@cross_origin()
def register_user():
    body = request.json
    token_id = get_token(request.headers)
    firebase_user = get_firebase_user(token_id)
    email = firebase_user.email
    return register_new_user(db, body["name"], body["surname"], email, body['birthdate'])

@app.route('/users/<user_id>/pay', methods=['POST'])
@cross_origin()
def pay(user_id: str):
    token_id = get_token(request.headers)

    if not is_user_authenticated(user_id, token_id):
        return abort(401)
    
    body = request.json
    if len(body['ticket_id']) > 0:
        return extend_ticket(db, body['ticket_id'], int(body['duration']), body['amount'])

    zone_id = db.collection("zones").where(filter=FieldFilter("name", "==", body['zone'])).get()[0].id
    if not zone_id:
        return abort(404, description="Zone not found")
    plate_id = db.collection("plates").where(filter=FieldFilter("number", "==", body['plate'])).where(filter=FieldFilter("user_id", "==", user_id)).get()[0].id
    if not plate_id:
        return abort(404, description="Plate not found")
    
    

    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(minutes=int(body['duration']) * 30)
    end_time.astimezone(timezone.utc)
    
    # print(f"Adding ticket for user {user_id}, plate {plate_id}, zone {zone_id}, payment method {body['payment_method_id']}, start time {start_time}, end time {end_time}, amount {body['amount']}")
    return add_ticket(db, user_id, plate_id, zone_id, body['payment_method_id'], start_time, end_time, float(body['amount']))

if __name__ == '__main__':
    app.run(port=5001)
