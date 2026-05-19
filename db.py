# db.py

import pymysql


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "hellowrold",
    "database": "ltodata",
    "port": 3306
}


def get_connection():

    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG["port"],
        cursorclass=pymysql.cursors.Cursor
    )