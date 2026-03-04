import time
import json
import os
import logging
from pathlib import Path
import mysql.connector
from escpos.printer import Usb
from dotenv import load_dotenv

logger = logging.getLogger('printer_worker')

priority_map = {
    0: "Low",
    1: "Medium",
    2: "High",
    3: "Very High"
}


class QueueDB:
    def __init__(self, config_path):
        load_dotenv()
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
            self.host = configs.get('mysql').get('host')
            print(self.host)
            self.user = configs.get('mysql').get('user')
            self.password = configs.get('mysql').get('password')
            self.database = configs.get('mysql').get('database')

            self.receipt_printer_VID = int(
                os.getenv("RECEIPT_PRINTER_VID"), 16)
            self.receipt_printer_VID = int(
                os.getenv("RECEIPT_PRINTER_PID"), 16)
            self.receipt_printer_VID = os.getenv("RECEIPT_PRINTER-TIMEOUT")

    def fetch_next_job(self):
        with mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database) as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1")
            job = cursor.fetchone()
            db.commit()
            return job

    def mark_job_status(self, job_id, status, fail_reason=None):
        with mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database) as db:
            cursor = db.cursor()
            cursor.execute(
                'UPDATE jobs Set status=%s fail_reason=%s WHERE id=%s', (status, fail_reason, job_id))
            db.commit()

    def job_funnel(self, job):
        printer = job.get(printer)
        if printer == 'receipt':
            self.receipt_funnel(job)
        else:
            self.mark_job_status(job['id'], 'failed')
            print(f"Failed Job {job['id']}: Invalid Printer")

    def receipt_funnel(self, job):
        job_type = job.get("job_type")
        if job_type == "task":
            self.print_task(job)
        elif job_type == 'message':
            self.print_Rmessage(job)
        elif job_type == 'shopping_list':
            self.print_Rshopping_list(job)
        else:
            self.mark_job_status(job['id'], 'failed')
            print(f"Failed Job {job['id']}: Invalid Receipt Job Type")

    def print_task(self, job):
        try:
            with Usb(self.receipt_printer_VID, self.receipt_printer_PID, self.receipt_printer_timeout) as receipt_printer:
                job_header = job.get('header')
                task_name = job_header.get('name')

                temp_priority = job_header.get('priority')
                task_priority = priority_map.get(temp_priority)

                task_deadline = job_header.get('deadline')
                task_desc = job.get("body")

                receipt_printer.set(bold=True)
                receipt_printer.text("="*42)
                receipt_printer.set(bold=True, double_height=2,
                                    double_width=2, align='left')
                receipt_printer.text(f"\n\n{task_name}\n")
                receipt_printer._raw(b'\x1B\x21\x00')
                receipt_printer.set(bold=True)
                receipt_printer.text(f"Priority: {task_priority}\n")
                if task_deadline:
                    receipt_printer.text(f"Deadline: {task_deadline}\n")
                if task_desc:
                    receipt_printer.text(f"{task_desc}\n")
                receipt_printer.text("\n\n")
                receipt_printer.print_and_feed()
                receipt_printer.print_and_feed()
                receipt_printer.print_and_feed()
                receipt_printer.print_and_feed()
                receipt_printer.print_and_feed()
                receipt_printer.text("="*42)
                receipt_printer.cut()
                self.mark_job_status(job['id'], 'done')
                print(f"Printed Job {job['id']}")

        except Exception as e:
            self.mark_job_status(job['id'], 'failed')
            print(f"Failed job {job['id']}: {e}")


queue = QueueDB('config.json')

if __name__ == '__main__':
    while True:
        job = queue.fetch_next_job()
        if job:
            prin
            queue.mark_job_status(job['id'], 'printing')
            queue.job_funnel(job)
        else:
            time.sleep(1)
