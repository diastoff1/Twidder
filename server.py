from flask import Flask, request, jsonify
from flask_sock import Sock
from flask_bcrypt import Bcrypt

import database_helper
import math
import random
import re

import hmac
import hashlib
from datetime import datetime, timezone 

app = Flask(__name__)
sock = Sock(app)
bcrypt = Bcrypt(app)

websockets = {} 

@app.before_request
def verify_hmac():
    # skip for the following routes
    if request.path in ['/','/sign_in', '/sign_up', '/ws'] or request.path.startswith('/static/'):
        return

    token = request.headers.get('Authorization')
    signature = request.headers.get('X-Signature')
    timestamp = request.headers.get('X-Timestamp')

    if not (token and signature and timestamp):
        return jsonify({'success': False, 'message': 'missing_security_headers'}), 401

    # valide for max of 100s
    current_time = datetime.now(timezone.utc).timestamp()
    if abs(current_time - int(timestamp)) > 100:
        return jsonify({'success': False, 'message': 'stale_request'}), 401

    # recompute HMAC signature
    secret = token.encode()  # token string to bytes
    payload = timestamp.encode() + request.get_data()  # timestamp + request body
    expected_sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    # compare signatures
    if not hmac.compare_digest(expected_sig, signature):
        return jsonify({'success': False, 'message': 'invalid_signature'}), 401

@app.route("/", methods = ['GET'])
def root():
    return app.send_static_file('client.html')

@app.teardown_request
def teardown(exception):
    database_helper.disconnect()

@sock.route("/ws")
def manage_websocket(ws):
    token = request.args.get('token')
    timestamp = request.args.get('timestamp')
    signature = request.args.get('signature')

    if not (token and timestamp and signature):
        ws.close()
        return

    # 1 minute for difference between the request and receivetime is the max acceptable
    try:
        current_time = datetime.now(timezone.utc).timestamp()
        if abs(current_time - int(timestamp)) > 60:
            ws.close()
            return
    except:
        ws.close()
        return

    #we encpde our parameters transforming string into bytes, reconstructing the signature
    secret = token.encode()
    payload = timestamp.encode()  
    expected_sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    # here we compare our reconstructed signature with the one we received
    if not hmac.compare_digest(expected_sig, signature):
        ws.close()
        return
    
    user = database_helper.find_user_by_token(token)
    if not user or not token:
        ws.close()
        return
    
    email = user['email']

    # we check if there is a connection with the same user in different browsers, if yes, close
    if email in websockets:
        try:
            websockets[email].send('logout')
            websockets[email].close()
        except:
            pass

    websockets[email] = ws

    # keep the conection
    try:
        while True:
            ws.receive()
    except:
        if token in websockets:
            del websockets[email]

def isvalid_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    m = re.match(pattern, email)
    if not m:
        return False
    return True

# to generate the token we use a random numbers from 
def generate_token():
    token_length = 36
    token = ""
    for i in range(token_length):
        token += chr(math.floor(random.random() * 26) + 97)
    return token

@app.route('/sign_in', methods = ['POST'])
def sign_in():
    #receive the information from the request
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'missing_fields'}), 400

    email = data['username']
    password = data['password']
    if not email or not password:
        return jsonify({'success': False, 'message': 'missing_fields'}), 400
    
    user = database_helper.find_user(email)
    if not user:
        return jsonify({'success': False, 'message': 'user_not_found'}), 401
    
    #hash the password received and then compare with the one stored in the db
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'success': False, 'message': 'wrong_password'}), 401
    else:
        new_token = generate_token()
        email = user['email']

        if email and email in websockets:
            try:
                websockets[email].send('logout')
                websockets[email].close()
                del websockets[email]
            except:
                pass

        database_helper.add_token(email, new_token)
        return jsonify({'success': True, 'message': 'Signed in', 'data': new_token}), 200

@app.route('/sign_up', methods = ['POST'])
def sign_up():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'no_data'}), 400
    
    
    email = data['email']
    password = data['password']
    firstname = data['firstname']
    familyname = data['familyname']
    gender = data['gender']
    city = data['city']
    country = data['country']
    
    if not email or not password  or not firstname or not familyname or not gender or not city or not country:
        return jsonify({'success': False, 'message': 'missing_fields'}), 400

    if not isvalid_email(email) or len(password) < 8:
        return jsonify({'success': False, 'message': 'incorrect_data'}), 400
    else:
        existing = database_helper.find_user(email)
        if existing:
            return jsonify({'success': False, 'message': 'user_exists'}), 409
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        database_helper.add_user(firstname, familyname, email, hashed_password, gender, city, country)
        return jsonify({'success': True, 'message': 'user_created'}), 201

@app.route('/sign_out', methods = ['DELETE'])
def sign_out():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'no_token'}), 400
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'invalid_token'}), 401

    database_helper.add_token(user['email'], "")

    email = user['email']
    if email in websockets:
        try:
            websockets[email].close()
            del websockets[email]
        except:
            pass

    return jsonify({'success': True, 'message': 'signed_out'}), 200


@app.route('/get_user_data_by_token', methods = ['GET'])
def get_user_data_by_token():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'no_token'}), 401
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'invalid_token'}), 401
    
    data = {
        'email': user['email'],
        'firstname': user['firstname'],
        'familyname': user['familyname'],
        'gender': user['gender'],
        'city': user['city'],
        'country': user['country']
    }
    return jsonify({'success': True, 'message': 'user_data_sent', 'data': data}), 200

@app.route('/get_user_data_by_email/<email>', methods = ['GET'])
def get_user_data_by_email(email):
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'no_token'}), 401
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'invalid_token'}), 401
    
    data = database_helper.find_user(email)
    if data == None:
        return jsonify({'success': False, 'message': 'user_not_found'}), 404

    
    data = {
        'email': data['email'],
        'firstname': data['firstname'],
        'familyname': data['familyname'],
        'gender': data['gender'],
        'city': data['city'],
        'country': data['country']
    }

    return jsonify({'success': True, 'message': 'user_data_sent', 'data': data}), 200

@app.route('/get_user_messages_by_token', methods = ['GET'])
def get_user_messages_by_token():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': "no_token"}), 401
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'invalid_token'}), 401
    
    user_id = user['id']
    messages = database_helper.get_messages_by_id(user_id)

    return jsonify({'success': True, 'message': "messages_sent", 'data': messages}), 200
    
@app.route('/get_user_messages_by_email/<email>', methods = ['GET'])
def get_user_messages_by_email(email):
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'no_token'}), 401
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'invalid_token'}), 401
    
    user_searched = database_helper.find_user(email)
    if not user_searched:
        return jsonify({'success': False, 'message': 'user_not_found'}), 404
    
    user_id = user_searched['id']
    #print("user searched id: " + str(user_id))
    
    messages = database_helper.get_messages_by_id(user_id)

    return jsonify({'success': True, 'message': 'messages_sent', 'data': messages}), 200


@app.route('/post_message', methods = ['POST'])
def post_message():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'no_token'}), 401
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'invalid_token'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'no_data'}), 400
    
    message = data.get('message')
    receiver_email = data.get('email')

    if not message or message.strip() == "" or not receiver_email:
        return jsonify({'success': False, 'message': 'empty_fields'}), 400
    
    receiver = database_helper.find_user(receiver_email)
    if not receiver:
        return jsonify({'success': False, 'message': 'email_not_found'}), 404
    
    #print(f"Posting Message: Sender {user['id']} -> Receiver {receiver['id']}")
    database_helper.post_message(user['id'], receiver['id'], message)
    return jsonify({'success': True, 'message': 'message_posted'}), 201


@app.route('/change_password', methods = ['PUT'])
def change_password():
    response = request.headers.get('Authorization')
    
    if not response:
        return jsonify({'success': False, 'message': 'no_token'}), 400
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'invalid_token'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'no_data'}), 400
    
    oldpassword = data.get('oldpassword')
    newpassword = data.get('newpassword')

    if not oldpassword or not newpassword:
        return jsonify({'success': False, 'message': 'missing_passwords'}), 400
    
    if not bcrypt.check_password_hash(user['password'], oldpassword):
        return jsonify({'success': False, 'message': 'wrong_password'}), 401
    
    if len(newpassword) < 8:
        return jsonify({'success': False, 'message': 'password_too_short'}), 400
    
    # hash the new password before saving
    hashed_newpassword = bcrypt.generate_password_hash(newpassword).decode('utf-8')
    database_helper.change_password(user['email'], hashed_newpassword) 
    
    return jsonify({'success': True, 'message': 'password_changed'}), 200


#if __name__ == '__main__':
    app.debug = True
    app.run()