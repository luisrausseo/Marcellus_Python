import csv
import sqlite3
import matplotlib
import numpy as np
import datetime as dt
db = sqlite3.connect(':memory:')

def init_db(cur):
    cur.execute('''CREATE TABLE wells (
        API VARCHAR(11),
        Latitude FLOAT,
        Longitude FLOAT,
        Spud_Date DATE)''')

def populate_db(cur, csv_fp):
    rdr = csv.reader(csv_fp)
    cur.executemany('''
        INSERT INTO wells (API, Latitude, Longitude, Spud_Date)
        VALUES (?,?,?,?)''', rdr)
#a = dt.date(2000,10,1)
#b=dt.datetime.strptime('3/5/1997','%d/%m/%Y')
cur = db.cursor()
init_db(cur)
populate_db(cur, open('wells2.csv'))
db.commit()

cur.execute("SELECT * FROM wells")
res = cur.fetchall()
print(res)
print(res[1000][3])
print(type(res[1000][3]))