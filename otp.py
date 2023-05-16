import pyotp
import datetime

secret_key = "E5TIQSWZCR7BWTA6DSXPLU7DZMTW5PIQ"
def generate_otp():
    totp = pyotp.TOTP(secret_key, interval=600)
    otp = totp.now()
    return otp

def verify_otp(otp):  
    totp = pyotp.TOTP(secret_key, interval=600)
    current_time = datetime.datetime.now()
    return totp.verify(otp, valid_window=1, for_time=current_time)


