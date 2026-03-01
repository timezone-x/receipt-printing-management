from datetime import date
import sqlite3
import json
from datetime import timedelta, datetime
from flask import Flask, jsonify, redirect, render_template, url_for, request, session
from escpos.printer import Usb


printer = Usb(
    0x04B8,
    0x0202,
    timeout=0
)
priority_map = {
    0: "Low",
    1: "Medium",
    2: "High",
    3: "Very High"
}


app = Flask(__name__)
app.secret_key = "jkpoJlkLMJplk0JL"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True


@app.route('/')
def index():
    pass


@app.route('/app/task')
def task():
    token = request.form.get('token')
    task_name = request.form.get('name')
    task_priority = request.form.get('priority')
    task_deadline = request.form.get('deadline')
    task_desc = request.form.get('desc')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
