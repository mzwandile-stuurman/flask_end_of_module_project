import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify, redirect, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS

class User(object):
    def __init__(self, id, username, password,user_email,phone_number,address):
        self.id = id
        self.username = username
        self.password = password
        self.user_email = user_email
        self.phone_number = phone_number
        self.address = address




def init_user_table():
    conn = sqlite3.connect('Point_of_Sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL, address TEXT NOT NULL, phone_number INT NOT NULL, user_email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_post_table():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_email TEXT NOT NULL,"
                     "password TEXT NOT NULL,"
                     "login_date TEXT NOT NULL)")
    print("Login table created successfully.")

def product_table():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL, date TEXT NOT NULL)")
    print("Product table created successfully.")


product_table()
init_user_table()
init_post_table()

def fetch_users():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4],data[5],data[6],data[7]))
    return new_data

users = fetch_users()

username_table = { u.username: u for u in users }
userid_table = { u.id: u for u in users }


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity



@app.route('/login/', methods=['GET','POST'])
def login():
    #username = request.form['username']
    #password = request.form['password']
    return render_template('/login.html')

@app.route('/enter-login/', methods = ['POST','GET'])
def register():
    return render_template('user-register.html')

@app.route('/get-image')
def image1():
    return render_template('image1_file.html')

@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        phone_number = request.form['phone_number']
        user_email = request.form['user_email']

        with sqlite3.connect("Point_of_Sale.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password,address,phone_number,user_email) VALUES(?, ?, ?, ?, ?, ?, ?)", (first_name, last_name, username, password,address,phone_number,user_email))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/create-products/', methods=["POST"])
@jwt_required()
def create_Point_of_Sale():
    response = {}

    if request.method == "POST":
        prod_name = request.form['prod_name']
        price = request.form['price']
        description = request.form['description']
        date_created = datetime.datetime.now()

        with sqlite3.connect('Point_of_Sale.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product("
                           "product_name,"
                           "price,"
                           "description,date) VALUES(?, ?, ?, ?)", (prod_name, price, description,date_created))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Point_of_Sale post added succesfully"
        return response

### Creating products

@app.route('/products/')
def show_products():
    print(request.is_json)

    return dict(request.json)




@app.route('/get-Point_of_Sales/', methods=["GET"])
def get_Point_of_Sales():
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM product")
        posts = cursor.fetchall()
        accumulator = []

        for i in posts:
           accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)

@app.route('/get-user/',methods=['GET'])
def view_profile():
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM user")
        posts = cursor.fetchall()
        accumulator = []

        for i in posts:
           accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)




@app.route("/delete-product/<int:post_id>")
@jwt_required()
def delete_product(post_id):
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(post_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product post deleted successfully."
    return response

@app.route('/update-product/<int:post_id>/', methods=["PUT"])
def edit_post(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('Point_of_Sale.db') as conn:
            incoming_data = dict(request.json)

            put_data = {}

            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")
                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE id=?", (put_data["price"], post_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response['status_code'] = 200
            if incoming_data.get("product_name") is not None:
                put_data['product_name'] = incoming_data.get('product_name')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET product_name =? WHERE id=?", (put_data["product_name"], post_id))
                    conn.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET description =? WHERE id=?", (put_data["description"], post_id))
                    conn.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200

    return response




if __name__ == '__main__':
    app.run(debug=True)
