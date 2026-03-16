import secrets
import mysql.connector
import os
from dotenv import load_dotenv


class TokenManager:
    def init(self):
        load_dotenv(self)
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_NAME = os.getenv("DB_NAME")

    def checkKey(self, key):
        with mysql.connector.connect(host=self.DB_HOST, user=self.DB_USER, password=self.DB_PASSWORD, database=self.DB_USER) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM auth_keys WHERE key=%s", (key,))
            key_check = cursor.fetchone()
            if key_check:
                return True
            else:
                return False

    def checkKeyPerm(self, key, permission):
        with mysql.connector.connect(host=self.DB_HOST, user=self.DB_USER, password=self.DB_PASSWORD, database=self.DB_USER) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM auth_keys WHERE key=%s", (key,))
            if cursor.fetchall():
                permissions = cursor.fetchall().get('permissions')
                if permission in permissions:
                    return True
                else:
                    return False

            else:
                return False
