import os
import uuid

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import firestore, credentials, auth
from firebase_admin.auth import UserNotFoundError
from flask import Flask, abort, request
from flask_cors import CORS, cross_origin

from common.enums import Role
from models.user import User

load_dotenv()

firestore_account_path = os.getenv('FIRESTORE_ACCOUNT_PATH')

# Application Default credentials are automatically created.
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
    return db.collection("users").where("email", "==", firebase_user.email).get()[0].to_dict()


@app.route('/users/<user_id>/payment-methods', methods=['POST'])
def add_payment_method(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    body = request.json()
    uuid4 = str(uuid.uuid4())
    method_ref = db.collection("payment-methods").document(uuid4)
    method_ref.set(body)
    return method_ref.get().to_dict()


@app.route('/users/<user_id>/payment-methods', methods=['GET'])
def get_payment_methods(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    user_payment_methods = db.collection('payment-methods').where("user", "==", user_id).get()
    return [i.to_dict() for i in user_payment_methods]


@app.route('/users/<user_id>/payment-methods/<payment_method_id>', methods=['DELETE'])
def remove_payment_method(user_id: str, payment_method_id: str):
    token_id = get_token(request.headers)
    method_ref = db.collection('payment-methods').document(payment_method_id)
    payment_method = method_ref.get().to_dict()
    if not is_user_authenticated(user_id, token_id) or payment_method["user_id"] != user_id:
        return abort(401)

    method_ref.delete()
    return True


@app.route('/users/<user_id>/tickets', methods=['GET'])
def get_tickets(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    user_tickets = db.collection('tickets').where("user", "==", user_id).get()
    return [i.to_dict() for i in user_tickets]


@app.route('/users/<user_id>/tickets', methods=['POST'])
def add_ticket(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    body = request.json()
    uuid4 = str(uuid.uuid4())
    ticket_ref = db.collection("tickets").document(uuid4)
    ticket_ref.set(body)
    return ticket_ref.get().to_dict()


@app.route('/users/<user_id>', methods=['PUT'])
def edit_user(user_id: str):
    token_id = get_token(request.headers)

    user = get_db_user_from_auth(get_firebase_user(token_id))
    user_to_edit_ref = db.collection("users").document(user_id)
    user_to_edit = user_to_edit_ref.get().to_dict()
    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.SERVICE_ADMINISTRATOR.value:
        return abort(401)
    # You cannot edit via APIs SYSTEM and SERVICE ADMINISTRATORS
    if user_to_edit["role"] == Role.SYSTEM_ADMINISTRATOR.value or user_to_edit[
        "role"] == Role.SERVICE_ADMINISTRATOR.value:
        abort(401)

    body = request.json
    user_to_edit_ref.set(body)
    return user_to_edit_ref.get().to_dict()


@app.route('/users/<user_id>', methods=['DELETE'])
def remove_user(user_id: str):
    token_id = get_token(request.headers)

    user = get_db_user_from_auth(get_firebase_user(token_id))
    user_to_delete_ref = db.collection("users").document(user_id)
    user_to_delete = user_to_delete_ref.get().to_dict()
    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.SERVICE_ADMINISTRATOR.value:
        return abort(401)
    # You cannot delete via APIs SYSTEM and SERVICE ADMINISTRATORS
    if user_to_delete["role"] == Role.SYSTEM_ADMINISTRATOR.value or user_to_delete[
        "role"] == Role.SERVICE_ADMINISTRATOR.value:
        abort(401)

    user_to_delete_ref.delete()
    return True


@app.route('/users/<user_id>/plates', methods=['GET'])
def get_plates(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    user_plates = db.collection('plates').where("user", "==", user_id).get()
    return [i.to_dict() for i in user_plates]


@app.route('/users/<user_id>/plates', methods=['POST'])
@cross_origin()
def add_plate(user_id: str):
    token_id = get_token(request.headers)
    if not is_user_authenticated(user_id, token_id):
        return abort(401)

    body = request.json

    uuid4 = str(uuid.uuid4())
    db.collection('plates').document(uuid4).set({"user_id": user_id, **body})

    return db.collection('plates').document(uuid4).get()


@app.route('/users/<user_id>/plates/<plate_id>', methods=['DELETE'])
def remove_plate(user_id: str, plate_id: str):
    token_id = get_token(request.headers)
    plate_ref = db.collection('plates').document(plate_id)
    plate = plate_ref.get().to_dict()
    if not is_user_authenticated(user_id, token_id) or plate["user_id"] != user_id:
        return abort(401)

    plate_ref.delete()
    return True


@app.route('/zones', methods=['GET'])
def get_zones():
    token_id = get_token(request.headers)
    # This line is only needed to check that the user is authenticated
    _ = get_firebase_user(token_id)
    result = db.collection('zones').get()
    return [i.to_dict() for i in result]


@app.route('/zones', methods=['POST'])
@cross_origin()
def add_zone():
    token_id = get_token(request.headers)

    user = get_db_user_from_auth(get_firebase_user(token_id))
    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.SERVICE_ADMINISTRATOR.value:
        return abort(401)
    body = request.json

    uuid4 = str(uuid.uuid4())
    db.collection('zones').document(uuid4).set(body)

    return db.collection('zones').document(uuid4).get()


@app.route('/zones/<zone_id>', methods=['DELETE'])
def remove_zone(zone_id: str):
    token_id = get_token(request.headers)

    user = get_db_user_from_auth(get_firebase_user(token_id))
    if user["role"] != Role.SYSTEM_ADMINISTRATOR.value or user["role"] != Role.SERVICE_ADMINISTRATOR.value:
        return abort(401)

    db.collection("zones").document(zone_id).delete()
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

    result = db.collection("users").where("email", "==", email).get()

    if len(result) == 0:
        return {
            "is_registered": False,
            "user_data": {}
        }
    return {"is_registered": True, "user_data": result[0].to_dict()}


@app.route('/register', methods=['POST'])
@cross_origin()
def register_user():
    body = request.json
    token_id = get_token(request.headers)
    firebase_user = get_firebase_user(token_id)
    email = firebase_user.email
    user = User(name=body["name"], surname=body["surname"], email=email, role=Role.CUSTOMER)
    db.collection("users").document(user.id).set(user.to_dict())
    return user.to_dict()


if __name__ == '__main__':
    app.run()
