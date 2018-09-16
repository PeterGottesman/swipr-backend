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

@app.route("/user/<uid>")
def user(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * from users WHERE uid = '{}'".format(uid))
    row = cursor.fetchone()
    if row is None:
        return None
    user = {
        "uid": row[0],
        "firstname": row[1],
        "lastname": row[2],
        "email": row[3],
        "photo": row[4],
        "bio": row[5],
        "rating": row[5],
        "td_id": row[6]
        }
    return user

def bids(buy):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bids WHERE buy = '{}'".format(buy))
    rows = cursor.fetchall()
    output = []
    for row in rows:
        output.append( {
            "id" : row[0],
            "buy" : row[1],
            "price" : row[2],
            "location" : row[3],
            "user" : user(row[4]),
            "timestamp" : str(row[5])
        })
    return output

@app.route("/buys", methods=["GET"])
def buys():
    return str(bids(True))
        
@app.route("/sells", methods=["GET"])
def sells():
    return str(bids(False))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
