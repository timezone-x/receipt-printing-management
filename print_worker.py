import time
import json
import os
import textwrap
import mysql.connector
from escpos.printer import Usb
from dotenv import load_dotenv


priority_map = {
    0: "Low",
    1: "Medium",
    2: "High",
    3: "Very High"
}


class QueueDB:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")

        self.receipt_printer_VID = int(
            os.getenv("RECEIPT_PRINTER_VID"), 16)
        self.receipt_printer_PID = int(
            os.getenv("RECEIPT_PRINTER_PID"), 16)
        self.receipt_printer_TIMEOUT = int(
            os.getenv("RECEIPT_PRINTER_TIMEOUT"))

    def open_receipt_printer(self):
        return Usb(self.receipt_printer_VID, self.receipt_printer_PID, self.receipt_printer_TIMEOUT)

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
            if fail_reason:
                cursor.execute(
                    'UPDATE jobs Set status=%s, fail_reason=%s WHERE id=%s', (status, fail_reason, job_id))
            else:
                cursor.execute(
                    'UPDATE jobs Set status=%s WHERE id=%s', (status, job_id))
            db.commit()

    def job_funnel(self, job):
        print("Routing Job")
        printer = job.get("printer")
        if printer == 'receipt':
            self.receipt_funnel(job)
            print("Job Routed! (Receipt)")
        else:
            self.mark_job_status(job['id'], 'failed', 'invalid printer')
            print(f"Failed Job {job['id']}: Invalid Printer")

    def receipt_funnel(self, job):
        print("Sub-routing Job")
        job_type = job.get("job_type")
        if job_type == "task":
            self.print_task(job)
            print("Job Sub-routed! (receipt-task)")
        elif job_type == 'message':
            self.print_Rmessage(job)
            print("Job Sub-routed! (receipt-message)")
        elif job_type == 'shopping_list':
            self.print_Rshopping_list(job)
            print("Job Sub-routed! (receipt-shopping-list)")
        else:
            self.mark_job_status(job['id'], 'failed',
                                 "Invalid receipt job type")
            print(f"Failed Job {job['id']}: invalid Receipt Job Type")

    def print_task(self, job):
        print(f"Printing Job {job['id']}")
        try:
            receipt_printer = self.open_receipt_printer()

            job_header = job.get('job_header')
            task_name = textwrap.fill(job_header.get('name'), width=21)

            temp_priority = job_header.get('priority')
            task_priority = priority_map.get(temp_priority)

            task_deadline = job_header.get('deadline')
            temp_task_desc = job.get("job_body")

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
            if temp_task_desc:
                task_desc = textwrap.fill(temp_task_desc, width=42)
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
            self.mark_job_status(job['id'], 'failed', fail_reason=e)
            print(f"Failed job {job['id']}: {e}")

        finally:
            receipt_printer.close()

    # def print_receipt_shopping_list(self, job):
    #     print(f"Printing Job {job['id']}")
    #     try:
    #         receipt_printer = self.open_receipt_printer()
    #         job_header = job.get('job_header')
    #         list_items = job.get('job_body')
    #         date = job.get('created_at').strftime("%x")
    #         receipt_printer.set(bold=True, double_height=2,
    #                             double_width=2, align='center')
    #         receipt_printer.text("SHOPPING LIST")
    #         receipt_printer._raw(b'\x1B\x21\x00')
    #         receipt_printer.text(f"Date: {date}")
    #         receipt_printer.text("="*42)
    #         receipt_printer.text("Items:")
    #         receipt_printer.set(bold=True)

    #         for i in list_items:


queue = QueueDB()

if __name__ == '__main__':
    while True:
        job = queue.fetch_next_job()
        if job:
            print("Job Found!")
            print("Converting Job header to JSON")
            print(job.get("job_header"))
            job['job_header'] = json.loads(job.get('job_header'))
            print(job)
            queue.mark_job_status(job['id'], 'printing')
            queue.job_funnel(job)
        else:
            time.sleep(1)
