from datetime import date
import json
from datetime import timedelta, datetime
from flask import Flask, jsonify, redirect, render_template, url_for, request, session
from escpos.printer import Usb
from queue_handler import QueueHandler


app = Flask(__name__)
app.secret_key = "jkpoJlkLMJplk0JL"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

print_queue = QueueHandler(config_path="config.json")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/app/task', methods=['POST', 'GET'])
def task():
    if request.method == 'POST':
        token = request.form.get('token')
        task_name = request.form.get('name')
        task_priority = request.form.get('priority')
        task_deadline = request.form.get('deadline')
        task_desc = request.form.get('desc')
        job_type = "task"
        job_header = {"name": task_name,
                      'priority': task_priority, "deadline": task_deadline}
        job_body = task_desc
        print_queue.add(job_type, job_header, job_body)
    elif request.method == 'GET':
        return render_template('task.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
