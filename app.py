import os
from datetime import timedelta
from urllib import response
from dotenv import load_dotenv
import bcrypt
from flask import Flask, jsonify, redirect, render_template, url_for, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from queue_handler import QueueHandler
from key_manager import KeyManager

load_dotenv()
app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])
app.secret_key = os.getenv("FLASK_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

print_queue = QueueHandler()
KM = KeyManager()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/receipt/task')
def render_task():
    return render_template('task.html')


@app.route('/receipt/message')
def render_message():
    return render_template('message.html')


@app.route('/api/receipt/task', methods=['POST'])
def task():
    token = request.args.get('token')
    if KM.checkKeyPerm(token, "task") == 200:
        sender = token
        task_name = request.json.get('name')
        task_priority = int(request.json.get('priority'))
        task_deadline = request.json.get('deadline')
        task_desc = request.json.get('description')
        printer = 'receipt'
        job_type = 'task'
        job_header = {
            'sender': sender,
            'name': task_name,
            'priority': task_priority,
            'deadline': task_deadline
        }
        job_body = task_desc
        print_queue.add(printer, job_type, job_header, job_body)
        return jsonify({'status': 200})
    else:
        return jsonify({"status": KM.checkKeyPerm(token, "task")})


@app.route('/api/receipt/message', methods=["POST"])
def message():
    token = request.args.get('token')
    if KM.checkKeyPerm(token, 'message') == 200:
        pass
    else:
        return jsonify({"status": KM.checkKeyPerm(token, 'message')})


@app.route('/api/userdata')
def fetch_userdata():
    token = request.args.get('token')
    if KM.checkKey(token):

        user_data = KM.getInfo(token)
        requested_data = request.args.get("req_data")
        response = {}
        for i in requested_data:
            pass
        return jsonify(KM.getInfo(token))
    else:
        return jsonify({"status": 401})

@app.route("/api/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    result = KM.login(user_id, password)
    if result == 200:
        session["user_id"] = user_id
        return redirect(url_for("index"))
    elif result == 401:
        return jsonify({"status": 401})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
