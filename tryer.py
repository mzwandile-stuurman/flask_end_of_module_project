'''import sqlite3
from flask import request
from flask import jsonify
con = sqlite3.connect("Point_of_Sale.db")

cursor = con.cursor()


#cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
cursor.execute("DROP TABLE product")
#print('Table dropped')


print(cursor.fetchall())'''




