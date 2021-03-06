import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def upload_file():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name ='dlqxdivje', api_key='599819111725767',
                      api_secret='lTD-aqaoTbzVgmZqyZxjPThyaVg')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        roomimage = request.files['room_image']
        app.logger.info('%s file_to_upload', roomimage)
        if roomimage:
            upload_result = cloudinary.uploader.upload(roomimage)
            app.logger.info(upload_result)
            return upload_result['url']


def fetch_users():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[1], data[2], data[4]))
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


users = fetch_users()


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


def init_hotel():
    with sqlite3.connect('users.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS hotel (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "room_name TEXT NOT NULL,"
                     "room_type TEXT NOT NULL,"
                     "room_image TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "room_view TEXT NOT NULL)")
    print("room table created successfully.")


class Booking(object):
    def __init__(self, room_name, room_type, price, room_view):
        self.room_name = room_name
        self.room_type = room_type
        self.price = price
        self.room_view = room_view


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
init_hotel()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kiyaamudienkhan@gmail.com'
app.config['MAIL_PASSWORD'] = 'Khanget69'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
CORS(app)


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        susername = request.json['username']
        slast_name = request.json['last_name']
        semail = request.json['email']
        spassword = request.json['password']


        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "username,"
                           "last_name,"
                           "email,"
                           "password) VALUES(?, ?, ?, ?)", (susername, slast_name, semail, spassword))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/login/', methods=['PATCH'])
def login():
    response = {}
    if request.method == "PATCH":
        emailaddress = request.json['email']
        # email = request.json["email"]
        passw = request.json['password']
        # password = request.json["password"]
        # print(email, password)

        with sqlite3.connect("users.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (emailaddress, passw))
            user = cursor.fetchone()

        response["status_code"] = 200
        response["data"] = user
        return response


@app.route('/all-users/', methods=["GET"])
def all_user():
    response = {}

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")

        response["status_code"] = 200
        response["description"] = "users retrieved successfully"
        response["data"] = cursor.fetchall()

    return response


@app.route("/delete-room/<int:room_id>")
def delete_room(room_id):
    response = {}
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hotel WHERE id=" + str(room_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "room deleted successfully."
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

                    if incoming_data.get("room_view") is not None:
                        put_data["room_view"] = incoming_data.get("room_view")
                        with sqlite3.connect('users.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE hotel SET room_view =? WHERE id=?",
                                           (put_data["room_view"], room_id))
                            conn.commit()
                            response['message'] = "Update was successfully added"
                            response['status_code'] = 200
                        return response
                    if incoming_data.get("room_view") is not None:
                        put_data['room_view'] = incoming_data.get('content')

                        with sqlite3.connect('users.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE hotel SET room_view =? WHERE id=?",
                                           (put_data["room_view"], room_id))
                            conn.commit()

                            response["room_view"] = "Booking updated successfully"
                            response["status_code"] = 200
                        return response
            return response
    return response


@app.route('/get-user/<int:users_id>/', methods=["GET"])
def get_user(users_id):
    response = {}

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id=" + str(users_id))

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
        response["description"] = "rooms retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/all-rooms/', methods=["GET"])
def all_room():
    response = {}

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotel")

        response["status_code"] = 200
        response["description"] = "rooms retrieved successfully"
        response["data"] = cursor.fetchall()

    return response


@app.route('/rooms/', methods=["POST", "GET"])
def rooms():
    response = {}
    if request.method == "GET":
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hotel")
            data = cursor.fetchall()
            response["message"] = "success"
            response["status_code"] = 201
            response['data'] = data
        return response

    if request.method == "POST":
        room_name = request.form['room_name']
        room_type = request.form['room_type']
        room_image = request.files['room_image']
        price = request.form['price']
        room_view = request.form['room_view']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO hotel("
                           "room_name,"
                           "room_type,"
                           "room_image,"
                           "price,"
                           "room_view) VALUES(?, ?, ?, ?, ?)", (room_name, room_type, upload_file(), price, room_view))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


if __name__ == '__main__':
    app.run()
