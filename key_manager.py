import secrets
import mysql.connector
import os
from dotenv import load_dotenv


class KeyManager:
    def __init__(self):
        load_dotenv()
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_NAME = os.getenv("DB_NAME")

    def checkKey(self, key):
        with mysql.connector.connect(host=self.DB_HOST, user=self.DB_USER, password=self.DB_PASSWORD, database=self.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM auth_keys WHERE auth_key = %s", (key,))
            key_check = cursor.fetchone()
            if key_check:
                return 200
            else:
                return 401

    def checkKeyPerm(self, key, permission):
        with mysql.connector.connect(host=self.DB_HOST, user=self.DB_USER, password=self.DB_PASSWORD, database=self.DB_NAME) as conn:
            cursor = conn.cursor()
            if self.checkKey(key) == 200:
                cursor.execute(
                    "SELECT permissions FROM auth_keys WHERE auth_key = %s", (key,))
                permissions = cursor.fetchone()[0]
                print(permission)
                print(permissions)
                if permission in permissions:
                    return 200
                else:
                    return 403
            else:
                return 401

    def getInfo(self, key):
        with mysql.connector.connect(host=self.DB_HOST, user=self.DB_USER, password=self.DB_PASSWORD, database=self.DB_NAME) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM auth_keys WHERE auth_key = %s", (key,))
            result = cursor.fetchone()
            print(f'KEY SEARCH RESULT: {result}')
            id = result.get("id")
            name = result.get("user")
            permissions = result.get("permissions")
            expiry = result.get("expiry")
            settings = result.get('settings')
            return {
                "id": id,
                "name": name,
                "permissions": permissions,
                "expiry": expiry,
                "settings": settings
            }
