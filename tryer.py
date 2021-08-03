import sqlite3
from flask import request
from flask import jsonify
def get_Point_of_Sales():
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM product")
        posts = cursor.fetchall()

    print(request.json)
get_Point_of_Sales()



