from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO, send
import os, json

app = Flask(__name__)
app.secret_key = 'secret123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
socketio = SocketIO(app)
PASSWORD = "AAP653"
USER_DB = 'usernames.json'

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, 'w') as f:
        json.dump(users, f)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        userid = request.form.get('userid')
        name = request.form.get('name')

        if password != PASSWORD:
            return "رمز اشتباهه!"

        users = load_users()
        if userid in users:
            session['name'] = users[userid]
        else:
            if not name.strip():
                return "اسم رو وارد کن!"
            users[userid] = name
            save_users(users)
            session['name'] = name

        session['userid'] = userid
        session['authenticated'] = True
        return redirect(url_for('chat'))

    return render_template('login.html')

@app.route('/chat')
def chat():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('chat.html', name=session['name'])

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return {'filename': file.filename}
    return 'No file uploaded', 400

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
