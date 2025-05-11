import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import firestore, credentials, auth
from flask import Flask, request, abort
from flask_cors import CORS

load_dotenv()

firestore_account_path = os.getenv('FIRESTORE_ACCOUNT_PATH')

# Application Default credentials are automatically created.
cred = credentials.Certificate(firestore_account_path)
firestore_app = firebase_admin.initialize_app(cred)
db = firestore.client()

#
# # TODO: Add firebase url
# FIREBASE_URL = os.getenv('FIREBASE_URL')
#
# # TODO: Add authentication
# firebase = firebase.FirebaseApplication(FIREBASE_URL, None)

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def get_firebase_user(token_id):
    decoded_token = auth.verify_id_token(token_id)
    user_id = decoded_token['uid']
    return auth.get_user(user_id)


def get_token(headers):
    token_id = headers.get('auth')

    if token_id is None:
        abort(401)
    print(token_id)
    return token_id


#
# @app.route('/zone-prices', methods=['GET'])
# def get_zone_prices():
#     token_id = get_token(request.headers)
#     return firebase.get('/zone-prices', None, params={"auth": token_id})
#
#
# @app.route('/payment-methods', methods=['GET'])
# def get_payment_methods():
#     token_id = get_token(request.headers)
#
#     return firebase.get('/payment-methods', None, params={"auth": token_id})
#
#
# @app.route('/tickets', methods=['GET'])
# def get_tickets():
#     token_id = get_token(request.headers)
#
#     return firebase.get('/tickets', None, params={"auth": token_id})
#
#
# @app.route('/profile', methods=['GET'])
# def get_profile():
#     token_id = get_token(request.headers)
#
#     return firebase.get('/profile', None, params={"auth": token_id})
#
#
# @app.route('/plates', methods=['GET'])
# def get_plates():
#     token_id = get_token(request.headers)
#
#     return firebase.get('/plates', None, params={"auth": token_id})
#
#
# @app.route('/users', methods=['POST'])
# def add_user():
#     token_id = get_token(request.headers)
#
#     body = request.json
#
#     return firebase.post('/users/add-user', body, params={"auth": token_id})
#
#
# @app.route('/users/<user_id>', methods=['DELETE'])
# def remove_user(user_id: int):
#     token_id = get_token(request.headers)
#
#     body = request.json
#
#     return firebase.post('/users/remove-user', body, params={"auth": token_id})
#
#
# @app.route('/users/<user_id>', methods=['PUT'])
# def edit_user(user_id: int):
#     token_id = get_token(request.headers)
#
#     body = request.json
#
#     return firebase.put('/users/edit-user', body, params={"auth": token_id})
#
#
# @app.route('/zones', methods=['POST'])
# def add_zone():
#     token_id = get_token(request.headers)
#
#     body = request.json
#
#     return firebase.post('/zones/add-zone', body, params={"auth": token_id})
#
#
# @app.route('/zones/<zone_id>', methods=['DELETE'])
# def remove_zone(zone_id: int):
#     token_id = get_token(request.headers)
#
#     body = request.json
#
#     return firebase.post('/zones/remove-zone', body, params={"auth": token_id})
#
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
# @app.route('/register', methods=['POST'])
# def add_zone():
#     token_id = get_token(request.headers)
#
#     body = request.json
#
#     return firebase.post('/register', body, params={"auth": token_id})


@app.route('/get-me', methods=['GET'])
def get_me():
    #token_id = get_token(request.headers)
    #user = get_firebase_user(token_id)
    # doc_ref = db.collection("users").document("alovelace")
    # doc_ref.set({"first": "Ada", "last": "Lovelace", "born": 1815})
    return "user"


if __name__ == '__main__':
    app.run()


