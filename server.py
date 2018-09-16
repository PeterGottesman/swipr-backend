#!/usr/bin/env python3

import pyodbc
import secrets
from flask import Flask

app = Flask(__name__)
conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+
                      secrets.url+';PORT=1433;DATABASE='+
                      secrets.db+';UID='+
                      secrets.username+';PWD='+
                      secrets.passwd)

@app.route("/")
def homepage():
    return "Tristan Wiley is a fake"

@app.route("/test", methods=["GET"])
def test():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES")
    rows = cursor.fetchall()
    if rows is None:
        return "Empty"
    return str([el for el in [row for row in rows]])

@app.route("/buys", methods=["GET"])
def buys():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bids WHERE buy = 1")
    rows = cursor.fetchall()
    return str(rows)

@app.route("/sells", methods=["GET"])
def sells():
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
