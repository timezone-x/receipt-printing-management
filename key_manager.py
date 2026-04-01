import secrets
import mysql.connector
import os
import secrets
import bcrypt
import json
from dotenv import load_dotenv
from pywin.dialogs import status


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
            user_settings = result.get('user_settings')
            return {
                "id": id,
                "name": name,
                "permissions": permissions,
                "expiry": expiry,
                "settings": settings,
                "user_settings": user_settings
            }


    def login(self, userid, password):
        with mysql.connector.connect(host=self.DB_HOST, user=self.DB_USER, password=self.DB_PASSWORD,
                                     database=self.DB_NAME) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM auth_keys WHERE id = %s", (userid,))
            user_data = cursor.fetchone()
            if user_data:
                user_password = user_data.get("password")
                if bcrypt.checkpw(password.encode("utf-8"), user_password.encode("utf-8")):
                    return 200
                else:
                    return 401
            else:
                return 401


    def create_user(self, password, perms, settings=None, user_settings=None, expiry=None, no_expiry=False):
        with mysql.connector.connect(host=self.DB_HOST, user=self.DB_USER, password=self.DB_PASSWORD,) as conn:
            cursor = conn.cursor()
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            auth_key = secrets.token_urlsafe(32)
            if no_expiry:
                vals = (hashed_password, auth_key, json.dumps(perms), json.dumps(settings), json.dumps(user_settings))
                cursor.execute("INSERT INTO auth_keys password, auth_key, expiry, permissions, settings, user_settings VALUES (%s, %s, NULL, %s, %s, %s) ", vals)
                conn.commit()
                user_id = cursor.lastrowid
                return {
                    status: 200,
                    id: user_id,
                }
            elif expiry:
                vals = (hashed_password, auth_key, expiry, json.dumps(perms), json.dumps(settings), json.dumps(user_settings))
                cursor.execute("INSERT INTO auth_keys password, auth_key, expiry, permissions, settings, user_settings VALUES (%s, %s, %s, %s, %s, %s) ", vals)
                conn.commit()
                user_id = cursor.lastrowid
                return {
                    status: 200,
                    id: user_id,
                }
            else:
                vals = (hashed_password, auth_key,json.dumps(perms), json.dumps(settings), json.dumps(user_settings))
                cursor.execute("INSERT INTO auth_keys password, auth_key,permissions, settings, user_settings VALUES (%s, %s, %s, %s, %s) ", vals)
                conn.commit()
                user_id = cursor.lastrowid
                return {
                    status: 200,
                    id: user_id,
