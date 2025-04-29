import os

from dotenv import load_dotenv
from firebase import firebase
from flask import Flask, request, abort

load_dotenv()

# TODO: Add firebase url
FIREBASE_URL = os.getenv('FIREBASE_URL')

# TODO: Add authentication
firebase = firebase.FirebaseApplication(FIREBASE_URL, None)

app = Flask(__name__)


def get_token(headers):
    token_id = request.headers.get('auth')

    if token_id is None:
        abort(401)

    return token_id


@app.route('/zone-prices', methods=['GET'])
def get_zone_prices():
    token_id = get_token(request.headers)
    return firebase.get('/zone-prices', None, params={"auth": token_id})


@app.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    token_id = get_token(request.headers)

    return firebase.get('/payment-methods', None, params={"auth": token_id})


@app.route('/tickets', methods=['GET'])
def get_tickets():
    token_id = get_token(request.headers)

    return firebase.get('/tickets', None, params={"auth": token_id})


@app.route('/profile', methods=['GET'])
def get_profile():
    token_id = get_token(request.headers)

    return firebase.get('/profile', None, params={"auth": token_id})


@app.route('/plates', methods=['GET'])
def get_plates():
    token_id = get_token(request.headers)

    return firebase.get('/plates', None, params={"auth": token_id})


@app.route('/users/add-user', methods=['POST'])
def add_user():
    token_id = get_token(request.headers)

    body = request.json

    return firebase.post('/users/add-user', body, params={"auth": token_id})


@app.route('/users/remove-user', methods=['POST'])
def remove_user():
    token_id = get_token(request.headers)

    body = request.json

    return firebase.post('/users/remove-user', body, params={"auth": token_id})


@app.route('/users/edit-user', methods=['PUT'])
def edit_user():
    token_id = get_token(request.headers)

    body = request.json

    return firebase.put('/users/edit-user', body, params={"auth": token_id})


@app.route('/users/add-zone', methods=['POST'])
def add_zone():
    token_id = get_token(request.headers)

    body = request.json

    return firebase.post('/zones/add-zone', body, params={"auth": token_id})


@app.route('/users/remove-zone', methods=['POST'])
def remove_zone():
    token_id = get_token(request.headers)

    body = request.json

    return firebase.post('/zones/remove-zone', body, params={"auth": token_id})


@app.route('/users/edit-zone', methods=['PUT'])
def edit_zone():
    token_id = get_token(request.headers)

    body = request.json

    return firebase.put('/zones/edit-zone', body, params={"auth": token_id})


@app.route('/users/register', methods=['POST'])
def add_zone():
    token_id = get_token(request.headers)

    body = request.json

    return firebase.post('/register', body, params={"auth": token_id})


if __name__ == '__main__':
    app.run()
