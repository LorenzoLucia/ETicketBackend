import os

from dotenv import load_dotenv
from firebase import firebase
from flask import Flask

load_dotenv()

# TODO: Add firebase url
FIREBASE_URL = os.getenv('FIREBASE_URL')

# TODO: Add authentication
firebase = firebase.FirebaseApplication(FIREBASE_URL, None)

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Rick è un frocio SIIIIIIIIIIII!'


if __name__ == '__main__':
    app.run()
