from flask_cors import CORS
from flask import Flask, jsonify, request, session,flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_socketio import SocketIO, emit
import sqlite3
import bcrypt
import os
import blockchain
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'super_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure CORS
CORS(app, resources={r"/*": {'origins': "*"}})

login_manager = LoginManager(app)


# Initialize the SQLite database
def init_db():
    print("blockchain.db initialized.")
    with sqlite3.connect('blockchain.db') as conn:
        cursor = conn.cursor()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS "main" (
                "id"	INTEGER,
                "previous_hash"	VARCHAR(255),
                "encrypted_data"	VARCHAR(1000),
                "current_hash"	INTEGER,
                PRIMARY KEY("id" AUTOINCREMENT)
            ); 
        """)
        conn.commit()

        cursor.execute('''
           CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    password TEXT NOT NULL,
    salt TEXT NOT NULL
);
        ''')
        conn.commit()


class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get_user_by_email(email):
        with sqlite3.connect('blockchain.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, password FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "password": user[3]
                }
            return None

@app.route("/check_buzzer",methods=["GET"])
def check_buzzer():
    pass

@app.route("/test")
def test():
    return "OK"
@app.route("/post_location",methods=["POST"])
def post_location():
    return request.data

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('blockchain.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(id=user[0], username=user[1], email=user[2])
    return None

def get_user_by_username(username):
    with sqlite3.connect('blockchain.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()
    
def get_user_by_email(email):
    with sqlite3.connect('blockchain.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Missing username, email, or password"}), 400

        if User.get_user_by_email(email) or get_user_by_username(username):
            return jsonify({"error": "Email or username already exists!"}), 409

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Insert the user into the database
        with sqlite3.connect('blockchain.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password, salt) 
                VALUES (?, ?, ?, ?)
            ''', (username, email, hashed_password.decode('utf-8'), salt.decode('utf-8')))
            conn.commit()

            # The above is for authentication purposes.
            # The code below creates tables for each user
            # so that it is easier to fetch the collision history,
            # location history of each user.
            new_user = blockchain.User(username)
            new_user.create_user()

        return jsonify({"message": "Registration successful! Please login."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Route for login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Fetch the user by email
    user = User.get_user_by_email(email)

    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            user_obj = User(id=user['id'], username=user['username'], email=user['email'])
            session["username"] = user['username']
            login_user(user_obj)  # Log the user in using Flask-Login
            return jsonify({"user": {"id": user['id'], "username": user['username'], "email": user['email']}}), 200
        else:
            return jsonify({"error": "Invalid password!"}), 401
    else:
        return jsonify({"error": "User not found!"}), 404

@app.route('/api/auth', methods=['GET'])
def auth():
    if current_user.is_authenticated:
        return jsonify({
            "isAuthenticated": True,
            "user": {
                "id": current_user.id, 
                "username": current_user.username,
                "email": current_user.email
            }
        })
    else:
        return jsonify({"isAuthenticated": False}),401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

@app.route('/fetch_all')
def return_all():
    user = blockchain.User(session["username"])
    return jsonify(user.fetch_data())

@app.route('/collision')
def return_collision():
    user = blockchain.User(session["username"])
    return jsonify(user.return_crash_data())

@app.route('/location')
def return_location():
    user = blockchain.User(session["username"])
    return jsonify(user.return_location_data())

@app.route('/add_data',methods=["POST"])
def add_data():
    logging.info(session)
    data = request.json
    user = blockchain.User(session["username"])
    user.add_data(data)
    return "Success"

@app.route('/send-notification/<message>')
def trigger_notification(message):
    socketio.emit('notification', {'message': message})
    return f"Notification '{message}' sent!"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

# receive location data from IoT.
# Note to self: if emit is used, 
# it'll possibly get sent from the IoT to the frontend directly as well. 
@socketio.on('location')
def location(location):
    print(location)
    user = blockchain.User(session["username"])
    user.add_data(location)


# the out of bounds message by socketio will be emitted 
# by the frontend for the IoT to recieve. so there needs to be no code needed 
# here at the backend.  



def out_of_bounds():
    return False

def in_forbidden():
    return False

# Event handler for disconnection
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    if "blockchain.db" not in os.listdir():
        init_db()
    socketio.run(app, host='0.0.0.0', debug=True, port=5000)
