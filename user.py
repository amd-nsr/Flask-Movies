from flask import current_app
from flask_login import UserMixin
from database import connect
from MySQLdb import escape_string as thwart

class User(UserMixin):
    def __init__(self, username, email, password):
        self.username = username
        self.emlail = email
        self.password = password
        self.active = True
        self.is_admin = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(username):
    cursor, connection = connect()
    cursor = connection.cursor()
    query = "SELECT EMAIL, PASSWORD FROM USER WHERE USERNAME = %s"
    cursor.execute(query, (username,))
    email, password = cursor.fetchone()
    user = User(username, email, password)
    #password = current_app.config["PASSWORDS"].get(user_id)
    #user = User(user_id, password) if password else None
    if user is not None:
        user.is_admin = user.username in current_app.config["ADMIN_USERS"]
    return user