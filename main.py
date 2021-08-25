import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify
# from flask_jwt import JWT, jwt_required, current_identity
from flask_mail import Mail, Message
from flask_cors import CORS
from flask import render_template, flash, redirect


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


def fetch_hotel():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotel")
        booking = cursor.fetchall()

        new_data = []

        for data in booking:
            new_data.append(Booking(data[1], data[2], data[3], data[4]))
    return new_data


# users = fetch_users()


def init_user_table():
    conn = sqlite3.connect('users.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "username TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_shop():
    with sqlite3.connect('users.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS shop (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "room_name TEXT NOT NULL,"
                     "room_type TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "room_size TEXT NOT NULL)")
    print("room table created successfully.")


class Booking(object):
    def __init__(self, room_name, room_type, price, room_size):
        self.room_name = room_name
        self.room_type = room_type
        self.price = price
        self.room_size = room_size


def fetch_rooms():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT *FROM room")
        rooms = cursor.fetchall()

        new_data = []

        for data in rooms:
            new_data.append(Booking(data[1], data[2], data[3], data[4]))
    return new_data


init_user_table()
init_shop()

username_table = { u.username: u for u in users }
user_id_table = { u.id: u for u in users }


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return user_id_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kiyaamudienkhan@gmail.com'
app.config['MAIL_PASSWORD'] = 'Khanget47'
app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = Truejwt = JWT(app, authenticate, identity)
CORS(app)
mail = Mail(app)

# jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        username = request.form['username']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "username,"
                           "last_name,"
                           "email,"
                           "password) VALUES(?, ?, ?, ?)", (username, last_name, email, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
            msg = Message('Hello Message', sender='kiyaamudienkhan@gmail.com',
                          recipients=[email])
            msg.body = 'My email using Flask'
            mail.send(msg)
        return response


@app.route("/delete-room/<int:post_id>")
@jwt_required()
def delete_room(room_id):
    response = {}
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hotel WHERE id=" + str(room_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "users room deleted successfully."
    return response


@app.route('/edit-booking/<int:room_id>', methods=["PUT"])
def edit_booking(room_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('users.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("room_name") is not None:
                put_data["room_name"] = incoming_data.get("room_name")
                with sqlite3.connect('users.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE hotel SET room_name =? WHERE id=?", (put_data["room_name"], room_id))
                    conn.commit()
                    response['message'] = "Update was successfully added"
                    response['status_code'] = 200
                return response
            if incoming_data.get("room_type") is not None:
                put_data['room_type'] = incoming_data.get('content')

                with sqlite3.connect('users.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE hotel SET room_type =? WHERE id=?", (put_data["room_type"], room_id))
                    conn.commit()

                    response["room_type"] = "Booking updated successfully"
                    response["status_code"] = 200
                return response
            if request.method == "PUT":
                with sqlite3.connect('users.db') as conn:
                    incoming_data = dict(request.json)
                    put_data = {}

                    if incoming_data.get("room_size") is not None:
                        put_data["room_size"] = incoming_data.get("room_size")
                        with sqlite3.connect('users.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE hotel SET room_size =? WHERE id=?",
                                           (put_data["room_size"], room_id))
                            conn.commit()
                            response['message'] = "Update was successfully added"
                            response['status_code'] = 200
                        return response
                    if incoming_data.get("room_size") is not None:
                        put_data['room_size'] = incoming_data.get('content')

                        with sqlite3.connect('users.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE hotel SET room_size =? WHERE id=?",
                                           (put_data["room_size"], room_id))
                            conn.commit()

                            response["room_size"] = "Booking updated successfully"
                            response["status_code"] = 200
                        return response
            return response
    return response


@app.route('/get-user/<int:post_id>/', methods=["GET"])
def get_user(post_id):
    response = {}

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotel WHERE id=" + str(post_id))

        response["status_code"] = 200
        response["description"] = "users retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/get-rooms/<int:id>/', methods=["GET"])
def get_rooms(id):
    response = {}

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotel WHERE id=" + str(id))

        response["status_code"] = 200
        response["description"] = "users retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)

@app.route('/all-rooms/', methods=["GET"])
def all_user():
    response = {}

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotel")

        response["status_code"] = 200
        response["description"] = "users retrieved successfully"
        response["data"] = cursor.fetchall()

    return response


@app.route('/rooms/', methods=["POST"])
def rooms():
    response = {}

    if request.method == "POST":

        room_name = request.form['room_name']
        room_type = request.form['room_type']
        price = request.form['price']
        room_size = request.form['room_size']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hotel("
                           "room_name,"
                           "room_type,"
                           "price,"
                           "room_size) VALUES(?, ?, ?, ?)", (room_name, room_type, price, room_size))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


if __name__ == '__main__':
    app.run()