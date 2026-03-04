import json
from pathlib import Path
import mysql.connector


class QueueHandler:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
            self.host = configs.get('mysql').get('host')
            self.user = configs.get('mysql').get('user')
            self.password = configs.get('mysql').get('password')
            self.database = configs.get('mysql').get('database')

    def add(self, printer, job_type, job_header, job_body):
        with mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database) as db:
            cursor = db.cursor()
            sql = "INSERT INTO jobs (printer, job_type, job_header, job_body) VALUES (%s, %s, %s, %s)"
            vals = (printer, job_type, str(job_header), job_body)
            cursor.execute(sql, vals)
            db.commit()
            print("added job to the queue")
