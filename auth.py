from db import db
import bcrypt
import jwt
from datetime import datetime, timedelta
from otp import generate_otp,verify_otp


password = "mysecretpassword"
salt = bcrypt.gensalt()
AdminCollection = db['Admin']
usersCollection = db['Users']


def signUp(email, password):
    # If user exists, return an error
    if AdminCollection.find_one({'email': email}):
        return {'status': 'error', 'message': 'User already exists'}
    AdminCollection.insert_one({
        'email': email,
        'password': bcrypt.hashpw(password.encode('utf-8'), salt)
    })
    return {'status': 'success', 'message': 'User signed up successfully'}


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
    user = AdminCollection.find_one({"email": email})
    if user:
        if bcrypt.checkpw(password.encode('utf8'), user['password']):
            # Generate a token if login is successful
            token = generate_token(email)
            return {'status': 'success', 'message': 'User logged in successfully', 'token': token}
    # Return an error response if login fails
    return {'status': 'error', 'message': 'Invalid email or password'}


def loginUser(email):
    user = usersCollection.find_one({"email": email})
    # if user not found insert one
    if not user:
        usersCollection.insert_one({'email': email})
    otp = generate_otp()
    usersCollection.update_one({'email': email}, {'$set': {'otp': otp}})

    # return message otp sent to email
    return {'status': 'success', 'message': 'OTP sent to your email', 'otp': otp}

def loginUserVerifyOtp(email,otp):
    user = usersCollection.find_one({"email": email})
    if user:
        if user['otp'] == otp:
            otpValid = verify_otp(otp)
            print('otp verified',otpValid)

            # if res is false, return an error
            if not otpValid:
                return {'status': 'error', 'message': 'OTP Expired'}

            # generate a token if login is successful
            token = generate_token(email)
            return {'status': 'success', 'message': 'User logged in successfully', 'token': token}
    # Return an error response if login fails
    return {'status': 'error', 'message': 'Invalid OTP'}
