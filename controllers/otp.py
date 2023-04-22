import random
import time
from models.index import OTP
from config.index import conn
from schemas.index import serializerList
import pymongo
from bson import ObjectId
# Define a dictionary to store the OTPs and their creation times
otp_dict = {}

# Define a function to generate a new OTP
def generate_otp():
    otp = ''
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp

# Define a function to check if an OTP has timed out
def is_otp_valid(otp):
    otp_dict = serializerList(conn.local.otp.find({"code": otp}))
    print(otp_dict)
    if not otp_dict or otp_dict[0]['expired'] == True:
        return False
    else:
        otp_time = otp_dict[0]['expiry_time']
        print(otp_time)
        current_time = time.time()
        print(current_time)
        if current_time - otp_time > 600:
            conn.dirums.otp.find_one_and_update({'_id': ObjectId(otp_dict[0]['_id'])}, {"$set": dict({'expired': True})})
            return False
        else:
            return True

# Define a function to generate and return a new OTP for a given user
def get_otp(user):
    # Check if the user already has a valid OTP
    otp_dict = serializerList(conn.dirums.otp.find({"issued_to": user}).sort('_id', pymongo.DESCENDING))
    if otp_dict and otp_dict[0]['issued_to'] == user and is_otp_valid(otp_dict[0]['code']):
       print(otp_dict[0]['code'])
       return {"otp sent"}
    
    # Generate a new OTP for the user
    otp = generate_otp()
    conn.dirums.otp.insert_one({'code': otp, "issued_to": user, "expiry_time": time.time() + 600, 'expired': False})
    print(otp)
    return {"otp sent"}

def verify_otp(otp, user):
    otp_dict = serializerList(conn.dirums.otp.find({"code": otp}).sort('_id', pymongo.DESCENDING))
    print(otp_dict)
    if otp_dict and otp != otp_dict[0]['code']:
        return False, "Invalid OTP"
    elif otp_dict and otp_dict[0]['issued_to'] != user:
        return False, "OTP does not match user"
    elif not otp_dict:
        return False, "Invalid OTP"
    elif not is_otp_valid(otp):
        return False, "OTP has expired"
    else:
        conn.dirums.otp.find_one_and_update({'_id': ObjectId(otp_dict[0]['_id'])}, {"$set": dict({'expired': True})})
        return True, "OTP verified"