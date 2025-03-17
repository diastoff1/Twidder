#    firstname varchar(120) not null,
#    familyname varchar(120) not null,
#    email varchar(120) not null,
#    password varchar(120) not null,
#    gender varchar(120) not null,
#    city varchar(120) not null,
#    country varchar(120) not null,
#    token varchar(36)

import sqlite3
from flask import g

DATABASE_URI = "database.db"

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
    
    return db

def disconnect():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()
        g.db = None

def get_messages_by_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                   select u.email, m.content
                   from messages m
                   join users u on m.receiver_id = u.id
                   where m.receiver_id = ?
                   order by m.id DESC
                   """, (user_id,))
    messages = cursor.fetchall()
    cursor.close()

    messages_array = []
    for message in messages:
        #print("Message: "+message[0] + "\n")
        messages_array.append({
            'writer': message[0],
            'content': message[1]
        })
    
    return messages_array

def find_user(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        data = {
            'id': user[0],
            'firstname': user[1],
            'familyname': user[2],
            'email': user[3],
            'password': user[4],
            'gender': user[5],
            'city': user[6],
            'country': user[7],
            'token': user[8]
            }
        return data
    else:
        return None

def find_user_by_token(token):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE token=?", (token,))
    user = cursor.fetchone()
    cursor.close()  

    if user:
        data = {
            'id': user[0],
            'firstname': user[1],
            'familyname': user[2],
            'email': user[3],
            'password': user[4],
            'gender': user[5],
            'city': user[6],
            'country': user[7],
            'token': user[8]
            }
        return data
    else:
        return None

def add_user(firstname, familyname, email, password, gender, city, country):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (firstname, familyname, email, password, gender, city, country) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (firstname, familyname, email, password, gender, city, country)
    )
    db.commit()
    cursor.close()

def add_token(email,token):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("update users set token=? where email=?", (token,email))
    db.commit()
    cursor.close()

def change_password(email, newpassword):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("update users set password=? where email=?", (newpassword,email))
    db.commit()
    cursor.close()

def post_message(sender_id, receiver_id, message):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO messages (writer_id, receiver_id, content) values (?, ?, ?)",
        (sender_id, receiver_id, message)
    )
    db.commit()
    cursor.close()