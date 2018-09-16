#!/usr/bin/env python3

# FAKE IT TILL YOU MAKE IT

import secrets
import pyodbc
import requests
import json
import random

conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+
                      secrets.url+';PORT=1433;DATABASE='+
                      secrets.db+';UID='+
                      secrets.username+';PWD='+
                      secrets.passwd)

payload = {"continuationToken":"",
           "minAge":17,
           "maxAge":23,
           "gender":None,
           "workActivity":None,
           "schoolAttendance":"College",
           "minIncome":None,
           "maxIncome":None}

userInsert = """INSERT INTO users (firstName, lastName, email,
photo, bio, rating, td_id) VALUES ('{givenName}', '{surname}',
'{email}', '{photo}', '{bio}', '{rating}', '{id}')"""

acctInsert = """INSERT INTO accounts VALUES('{id}', '{uid}')"""



locations = [
    "Student Union",
    "Moes",
    "Pistacios",
    "Au Bon Pain",
    "Sizzles",
    "Goodyear"
]

with open("pics.txt") as f:
    pics = f.readlines()

def getUsers(numPages):
    users = []
    for page in range(numPages):
        response = requests.post('https://api.td-davinci.com/api/simulants/page',
                                 headers = { 'Authorization': secrets.tdKey },
                                 json = payload)
        response_data = response.json()
        users += response_data["result"]["customers"]
        payload["continuationToken"] = response_data["result"]["continuationToken"]
        print("Have gotten {} of {} pages".format(page+1, numPages))
    return users

def getAccts(user):
    url = "https://api.td-davinci.com/api/customers/{id}/accounts"
    response = requests.get(url.format(**user),
                             headers = { 'Authorization': secrets.tdKey })
    response_data = response.json()
    return response_data

def insertUser(user):
    cursor = conn.cursor()
    cursor.execute(userInsert
                   .format(**user, rating=random.randrange(3,6),
                           email="fake@gmail.com",
                           bio="Hi", photo=random.choice(pics)))
    accts = getAccts(user)["result"]
    for acctType in accts:
        if accts[acctType] is None:
            continue
        for acct in accts[acctType]:
            cursor.execute(acctInsert.format(id=acct["id"],
                                             uid=user["id"]))

    cursor.commit()

bidInsert = """INSERT INTO bids (buy, price, location, uid, timestamp)
VALUES ('{buy}', '{price}', '{location}', '{uid}', GETDATE())"""

def makeBids(count):
    cursor = conn.cursor()
    for i in range(count):
        cursor.execute(bidInsert.format(buy=random.choice([0,1]),
                               price=random.uniform(4, 8),
                               location=random.choice(locations),
                               uid=random.randrange(0,100)))
    cursor.commit()

def changePhotos():
    cursor = conn.cursor()
    for i in range(100):
        cursor.execute("UPDATE users SET photo = '{pic}' WHERE uid='{uid}'"
                       .format(pic=random.choice(pics),
                               uid=i+1))

    cursor.commit()

if __name__ == "__main__":
    # users = getUsers(10)
    # for user in users:
    #     insertUser(user)
#    makeBids(15)
    changePhotos()
