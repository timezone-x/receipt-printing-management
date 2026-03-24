import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, url_for, request, session
from queue_handler import QueueHandler
from key_manager import KeyManager

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

print_queue = QueueHandler()
KM = KeyManager()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/receipt/task')
def task():
    return render_template('task.html')


@app.route('/api/receipt/task', methods=['POST'])
def api_task():
    token = request.args.get('token')
    if KM.checkKeyPerm(token, "task") == 200:
        key_info = KM.getInfo(token)
        sender = key_info.get("name")
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
