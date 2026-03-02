import time
import json
from pathlib import Path
import mysql.connector
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


class QueueDB:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
            self.host = configs.get('host')
            self.user = configs.get('user')
            self.password = configs.get('password')
            self.database = configs.get('database')

    def fetch_next_job(self):
        with mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database) as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1")
            job = cursor.fetchone()
            db.commit()
            return job

    def mark_job_status(self, job_id, status):
        with mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database) as db:
            cursor = db.cursor()
            cursor.execute(
                'UPDATE jobs Set status=%s WHERE id=%s', (status, job_id))
            db.commit()

    def print_job(self, job):
