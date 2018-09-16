#!/usr/bin/env python3

import pyodbc
import json
import secrets
from flask import Flask, request

app = Flask(__name__)
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+
                      secrets.url+';PORT=1433;DATABASE='+
                      secrets.db+';UID='+
                      secrets.username+';PWD='+
                      secrets.passwd)

@app.route("/")
def homepage():
    return "Tristan Wiley is a fake"

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
        "rating": float(row[6]),
        "td_id": row[7]
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
            "price" : float(row[2]),
            "location" : row[3],
            "user" : user(row[4]),
            "timestamp" : str(row[5])
        })
    return output

@app.route("/buys", methods=["GET"])
def buys():
    return json.dumps(bids(True))
        
@app.route("/sells", methods=["GET"])
def sells():
    return json.dumps(bids(False))

@app.route("/user/<uid>")
def pubUser(uid):
    return json.dumps(user(uid))

def createBid(buy, price, location, uid):
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO bids VALUES
('{buy}', '{price}', '{location}', '{uid}', GETDATE())"""
                   .format(buy=buy,price=price,location=location,uid=uid))
    cursor.commit()
#    return cursor.execute("SELECT max(id) FROM bids").fetchone()

def completeTransaction(bidId):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bids WHERE id={}"
                   .format(bidId))
    row = cursor.fetchone()
    if row is None or len(row) == 0:
        return None
    
    newBid = createBid(*row)

    cursor.execute(""""INSERT INTO transactions
""")
    return

@app.route("/bid/place", methods=["POST"])
def makeBidPub():
    # turn into json to resolve booleans
    in_json = request.get_json()
    sender = int(in_json["sender"])
    buy = in_json["buy"]
    price = float(in_json["price"])
    location = in_json["location"]
    print(in_json)
    createBid(buy, price, location, sender)
    if buy:
        return buys()
    return sells()
    

# @app.route("/messaging/complete", methods=["POST"])
# def complete():
    

@app.route("/messaging/send",methods=["POST"])
def sendMsg():
    in_json = request.get_json()
    sender = int(in_json["sender"])
    partner = int(in_json["partner"])
    content = in_json["content"]
    cursor = conn.cursor()
    cursor.execute("""IF NOT EXISTS
(SELECT id FROM chat WHERE (user1 = {u1} AND user2 = {u2}) OR (user1 = {u2} AND user2 = {u1}))
INSERT INTO chat VALUES ('{u1}', '{u2}', null)"""
    .format(u1=sender, u2=partner))

    cursor.commit()
    
    cursor.execute("""
INSERT INTO messages
VALUES ({sender}, (SELECT id FROM chat WHERE (user1 = {u1} AND user2 = {u2}) OR (user1 = {u2} AND user2 = {u1})),
 '{content}', GETDATE())"""
                   .format(sender=sender, u1=sender, u2=partner, content=content))
    cursor.commit()
    return getMessages(sender, partner)
    
                    
@app.route("/messaging/receive/<u1>/<u2>", methods=["GET"])
def getMessages(u1, u2):
    cursor = conn.cursor()
    cursor.execute("""SELECT * from messages mess
INNER JOIN
(
SELECT id FROM chat WHERE (user1 = {u2} AND user2 = {u1})
OR (user1 = {u1} AND user2 = {u2})
) chats
ON chats.id = mess.chat
"""
                   .format(u1=u1, u2=u2))
    messages = cursor.fetchall()
    output = []
    for message in messages:
        output.append({
            "id": message[0],
            "sender": user(message[1]),
            "chat": message[2],
            "content": message[3],
            "timestamp": str(message[4])
            })
    return json.dumps(output)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
