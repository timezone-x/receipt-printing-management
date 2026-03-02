import json
from pathlib import Path
import mysql.connector


class QueueHandler:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
            self.host = configs.get('host')
            self.user = configs.get('user')
            self.password = configs.get('password')
            self.database = configs.get('database')

    def add(self, job_type, job_header, job_body):
        with mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database) as db:
            cursor = db.cursor()
            sql = "INSERT INTO jobs (job_type, job_header, job_body) VALUES (%s, %s, %s)"
            vals = (job_type, job_header, job_body)
            cursor.execute(sql, vals)
            db.commit()
            print("added job to the queue")
