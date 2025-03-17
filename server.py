from flask import Flask, request, jsonify
from flask_sock import Sock

import database_helper
import math
import random
import re

app = Flask(__name__)
sock = Sock(app)
websockets = {} 


    


@app.route("/", methods = ['GET'])
def root():
    return app.send_static_file('client.html')

@app.teardown_request
def teardown(exception):
    database_helper.disconnect()

@sock.route("/ws")
def manage_websocket(ws):
    token = request.args.get('token')

    if token and token.strip():
        user = database_helper.find_user_by_token(token)
    if not user or not token:
        ws.close()
        return
    
    email = user['email']

    if email in websockets:
        try:
            websockets[email].send('logout')
            websockets[email].close()
        except:
            pass

    websockets[email] = ws

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

def generate_token():
    token_length = 36
    token = ""
    for i in range(token_length):
        token += chr(math.floor(random.random() * 26) + 97)
    return token

@app.route('/sign_in', methods = ['POST'])
def sign_in():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 200

    email = data['username']
    password = data['password']

    user = database_helper.find_user(email)
    if not user:
        return jsonify({'success': False, 'message': 'User does not exist'}), 200
    
    if user['password'] != password:
        return jsonify({'success': False, 'message': 'Wrong password'}), 200
    elif user['password'] == password:
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
        return jsonify({'success': False, 'message': 'No data provided'}), 200
    
    email = data['email']
    password = data['password']
    firstname = data['firstname']
    familyname = data['familyname']
    gender = data['gender']
    city = data['city']
    country = data['country']

    if not email or not isvalid_email(email) or not password or len(password) < 8 or not firstname or not familyname or not gender or not city or not country:
        return jsonify({'success': False, 'message': 'Incorrect data'}), 200
    else:
        existing = database_helper.find_user(email)
        if existing:
            return jsonify({'success': False, 'message': 'User already exists'}), 200
        database_helper.add_user(firstname, familyname, email, password, gender, city, country)
        return jsonify({'success': True, 'message': 'User created'}), 200

@app.route('/sign_out', methods = ['DELETE'])
def sign_out():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'No token provided'}), 200
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'Incorrect token'}), 200

    database_helper.add_token(user['email'], "")

    email = user['email']
    if email in websockets:
        try:
            websockets[email].close()
            del websockets[email]
        except:
            pass

    return jsonify({'success': True, 'message': 'Signed out'}), 200


@app.route('/get_user_data_by_token', methods = ['GET'])
def get_user_data_by_token():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'No token provided'}), 200
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'Incorrect token'}), 200
    
    data = {
        'email': user['email'],
        'firstname': user['firstname'],
        'familyname': user['familyname'],
        'gender': user['gender'],
        'city': user['city'],
        'country': user['country']
    }
    return jsonify({'success': True, 'message': 'User data sent', 'data': data}), 200

@app.route('/get_user_data_by_email/<email>', methods = ['GET'])
def get_user_data_by_email(email):
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'No token provided'}), 200
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'Incorrect token'}), 200
    
    data = database_helper.find_user(email)
    if data == None:
        return jsonify({'success': False, 'message': 'User does not exist'}), 200

    
    data = {
        'email': data['email'],
        'firstname': data['firstname'],
        'familyname': data['familyname'],
        'gender': data['gender'],
        'city': data['city'],
        'country': data['country']
    }

    return jsonify({'success': True, 'message': email + ' data sent', 'data': data}), 200

@app.route('/get_user_messages_by_token', methods = ['GET'])
def get_user_messages_by_token():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': "No token provided"}), 200
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'Incorrect token'}), 200
    
    user_id = user['id']
    messages = database_helper.get_messages_by_id(user_id)

    return jsonify({'success': True, 'message': "Messages sent", 'data': messages}), 200
    
@app.route('/get_user_messages_by_email/<email>', methods = ['GET'])
def get_user_messages_by_email(email):
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'No token provided'}), 200
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'Incorrect token'}), 200
    
    user_searched = database_helper.find_user(email)
    if not user_searched:
        return jsonify({'success': False, 'message': 'User does not exist'}), 200
    
    user_id = user_searched['id']
    #print("user searched id: " + str(user_id))
    
    messages = database_helper.get_messages_by_id(user_id)

    return jsonify({'success': True, 'message': email + ' messages sent', 'data': messages}), 200


@app.route('/post_message', methods = ['POST'])
def post_message():
    response = request.headers.get('Authorization')
    if not response:
        return jsonify({'success': False, 'message': 'No token provided'}), 200
    
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'Incorrect token'}), 200
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 200
    
    message = data.get('message')
    receiver_email = data.get('email')

    if not message or message.strip() == "" or not receiver_email:
        return jsonify({'success': False, 'message': 'Empty field(s)'}), 200
    
    receiver = database_helper.find_user(receiver_email)
    if not receiver:
        return jsonify({'success': False, 'message': 'Email not found'}), 200
    
    #print(f"Posting Message: Sender {user['id']} -> Receiver {receiver['id']}")
    database_helper.post_message(user['id'], receiver['id'], message)
    return jsonify({'success': True, 'message': 'Message posted'}), 200


@app.route('/change_password', methods = ['PUT'])
def change_password():
    response = request.headers.get('Authorization')
    
    if not response:
        return jsonify({'success': False, 'message': 'No token provided'}), 200
    user = database_helper.find_user_by_token(response)
    if not user:
        return jsonify({'success': False, 'message': 'Incorrect token'}), 200
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 200
    
    oldpassword = data.get('oldpassword')
    newpassword = data.get('newpassword')

    #print(oldpassword)
    #print(newpassword)

    if not oldpassword or not newpassword:
        return jsonify({'success': False, 'message': 'Missing one or both passwords'}), 200
    
    if oldpassword != user['password']:
        return jsonify({'success': False, 'message': 'Incorrect password'}), 200
    
    if len(newpassword) < 8:
        return jsonify({'success': False, 'message': 'Password too short'}), 200
    
    database_helper.change_password(user['email'], newpassword)
    return jsonify({'success': True, 'message': 'Password changed'}), 200


#if __name__ == '__main__':
    app.debug = True
    app.run()