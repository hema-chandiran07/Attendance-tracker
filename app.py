from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from flask import send_from_directory
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# MySQL connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='hema2006',
        database='attendance_db'
    )

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], role=user[3])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):
            user_obj = User(id=user[0], username=user[1], role=user[3])
            login_user(user_obj)
            return redirect(url_for('index'))

        flash("Invalid credentials, please try again.", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Logs the user out
    return redirect(url_for('login'))  # Redirects to login page


@app.route('/')
@login_required
def index():
    return render_template('index.html', role=current_user.role)

@app.route('/add', methods=['POST'])
@login_required
def add_attendance():
    if current_user.role != 'staff':
        flash('You do not have permission to add attendance.', 'danger')
        return redirect(url_for('index'))

    name = request.form['name']
    status = request.form['status']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO attendance (name, status) VALUES (%s, %s)', (name, status))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/attendance', methods=['GET'])
@login_required
def get_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC')
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(records)

# Route to register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # 'staff' or 'student'

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already taken. Please choose a different one.', 'danger')
        else:
            # Insert new user
            cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, hashed_password, role))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        cursor.close()
        conn.close()

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)








