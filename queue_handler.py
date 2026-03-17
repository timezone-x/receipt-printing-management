import os
from dotenv import load_dotenv
import mysql.connector


class QueueHandler:
    def __init__(self,):
        load_dotenv()
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")

    def add(self, printer, job_type, job_header, job_body):
        with mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database) as db:
            cursor = db.cursor()
            sql = "INSERT INTO jobs (printer, job_type, job_header, job_body) VALUES (%s, %s, %s, %s)"
            vals = (printer, job_type, str(
                job_header).replace("'", '"'), job_body)
            cursor.execute(sql, vals)
            db.commit()
            print("added job to the queue")
