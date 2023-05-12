from db import db
import bcrypt
import jwt
from datetime import datetime, timedelta


password = "mysecretpassword"
salt = bcrypt.gensalt()
collection = db['users']

def signUp(email, password):
    collection.insert_one({
        'email': email,
        'password': bcrypt.hashpw(password.encode('utf-8'), salt)
    })


def generate_token(email):
    # Set token expiry time to 30 minutes
    expiry_time = datetime.utcnow() + timedelta(minutes=30)

    # Create the payload for the token
    payload = {
        'email': email,
        'exp': expiry_time
    }

    # Encode the payload with the secret key to generate the token
    token = jwt.encode(payload, password, algorithm='HS256')

    # Return the generated token
    return token

def validate_token(token):
    try:
        payload = jwt.decode(token, password, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def login(email, password):
    user = collection.find_one({"email": email})
    if user:
        if bcrypt.checkpw(password.encode('utf8'), user['password']):
            # Generate a token if login is successful
            token = generate_token(email)
            return {'status': 'success', 'message': 'User logged in successfully', 'token': token}
    # Return an error response if login fails
    return {'status': 'error', 'message': 'Invalid email or password'}
