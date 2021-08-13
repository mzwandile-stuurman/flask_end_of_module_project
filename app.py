####-------- MZWANDILE STUURMAN FALSK END OF MODULE ----------####

# Importing all necessary modules
import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify, redirect, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail,Message
from smtplib import SMTPRecipientsRefused, SMTPAuthenticationError
from werkzeug.utils import redirect




# defining class for user authantication
class User(object):
    def __init__(self, id, username, password,user_email,phone_number,address):
        self.id = id
        self.username = username
        self.password = password
        self.user_email = user_email
        self.phone_number = phone_number
        self.address = address



# creating a database table for user registration
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

# creating a login table
def init_login_table():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_email TEXT NOT NULL,"
                     "password TEXT NOT NULL,"
                     "login_date TEXT NOT NULL)")
    print("Login table created successfully.")

# creating the product table
def product_table():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "price INT NOT NULL,"
                     "description TEXT NOT NULL, date TEXT NOT NULL, image TEXT NOT NULL)")
    print("Product table created successfully.")


product_table()
init_user_table()
init_login_table()

# fecth username and surname for user authentication
def fetch_users():
    with sqlite3.connect('Point_of_Sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4],data[5],data[6],data[7])) # append all data to new_data empty list
    return new_data

users = fetch_users() # declare users tables to a variable "users"

username_table = { u.username: u for u in users } # make a dictionary for username
userid_table = { u.id: u for u in users } # make a dictionary for user id

# set authantication for username and password
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

# identify registered user by user id
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)

# setting up flask-mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'stuurmanmzwandile@gmail.com'
app.config['MAIL_PASSWORD'] = '@strmzw001'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

#authanticate a loggen in user
jwt = JWT(app, authenticate, identity)
@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity
# home page
@app.route('/')
def welcome_page():
    return "<h1>Welcome to Yocco</h1>"
        #render_template('image1_file.html')

# end-point to register a user
@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}
    if request.method == "POST":
        try:
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
                msg = Message("Registered successfuly!!", sender = "mzwandilestuurman@gmia.com", recipients=[user_email])
                msg.body = "Please login  to enjoy our services."
                return response
        except SMTPRecipientsRefused:
            response["message"] = "Invalid email used"
            response["status_code"] = 401
            return response
        except SMTPAuthenticationError:
            response["message"] = "Incorrect login details"
            response["status_code"] = 401
            return response

@app.route('/user-login/', methods=["POST"])
def user_login():
    response = {}
    if request.method == "POST":
        try:

            user_email = request.form['user_email']
            password = request.form['password']
            date_created = datetime.datetime.now()

            with sqlite3.connect("Point_of_Sale.db") as conn:
                cursor = conn.cursor()


                cursor.execute("INSERT INTO login("
                               "user_email,"
                               "password,"
                               "login_date) VALUES(?, ?, ?)", (user_email, password, date_created))
                conn.commit()
                response["message"] = "success"
                response["status_code"] = 201

                return  response
        except SMTPRecipientsRefused:
            response["message"] = "Invalid email used"
            response["status_code"] = 401
            return response
        except SMTPAuthenticationError:
            response["message"] = "Incorrect login details"
            response["status_code"] = 401
            return response


# create a product
@app.route('/create-products/', methods=["POST"])
#@jwt_required # authantication required
def create_Point_of_Sale():
    response = {}

    if request.method == "POST":
        try:

            prod_name = request.form['prod_name']
            price = request.form['price']
            description = request.form['description']
            image = request.form['image']
            date_created = datetime.datetime.now()

            with sqlite3.connect('Point_of_Sale.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO product("
                               "product_name,"
                               "price,"
                               "description,image,date) VALUES(?, ?, ?, ?,?)", (prod_name, price, description,image,date_created))
                conn.commit()
                response["status_code"] = 201
                response['description'] = "Product added succesfully"
                return response

        except Exception:
            response['message'] = "You created an invalid product"
            response['status_code'] = 400
            return response

### Creating products
@app.route('/get-Point_of_Sales/', methods=["GET"])
def get_Point_of_Sales():
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row # cursor to capture table headings
        cursor.execute("SELECT * FROM product")
        posts = cursor.fetchall() # fecth all fields in the product table
        accumulator = []

        for i in posts:
           accumulator.append({k: i[k] for k in i.keys()}) # return table a dictionary

    response['status_code'] = 200
    response['data'] = tuple(accumulator) # insert data into response
    return jsonify(response)

# end-point to get all users
@app.route('/get-users/',methods=['GET'])
def view_all_users():
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

# get a single user
@app.route("/single-user/<int:user_id>", methods=['GET'])
def get_single_user(user_id):
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM user WHERE user_id=" + str(user_id))
        posts = cursor.fetchall()
        accumulator = []
        for i in posts:
           accumulator.append({k: i[k] for k in i.keys()})
        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        response['message'] = " User selected successfully"
    return jsonify(response)

# get single product
@app.route("/single-product/<int:post_id>", methods=['GET'])
def get_single_product(post_id):
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM product WHERE id=" + str(post_id))
        posts = cursor.fetchall()
        accumulator = []
        for i in posts:
           accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        response['message'] = "Product successfully."
    return jsonify(response)

# delete product by id
@app.route("/delete-product/<int:post_id>")
#@jwt_required()
def delete_product(post_id):
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(post_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product post deleted successfully."
    return response

@app.route("/delete-product-front/", methods=['POST'])
#@jwt_required()
def delete_product_front():
    response = {}
    if request.method == "POST":
        try:

            post_id = request.form['id']
            with sqlite3.connect("Point_of_Sale.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM product WHERE id=" + str(post_id))
                conn.commit()
                response['status_code'] = 200
                response['message'] = "Product post deleted successfully."
            return response
        except Exception:
            response['message'] = "You created an invalid product"
            response['status_code'] = 400
            return response

# update product by a particula column
@app.route('/update-product/<int:post_id>/', methods=["PUT"])
def edit_post(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('Point_of_Sale.db') as conn:
            incoming_data = dict(request.json)

            put_data = {}

            if incoming_data.get("price") is not None: # check if the updated column is price
                put_data["price"] = incoming_data.get("price")
                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE id=?", (put_data["price"], post_id))
                    conn.commit()
                    response['message'] = "Product price was successful"
                    response['status_code'] = 200
            if incoming_data.get("product_name") is not None:
                put_data['product_name'] = incoming_data.get('product_name')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET product_name =? WHERE id=?", (put_data["product_name"], post_id))
                    conn.commit()

                    response["content"] = "Product name updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET description =? WHERE id=?", (put_data["description"], post_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

    return response

# update a single user
@app.route('/update-user/<int:post_id>/', methods=["PUT"])
def edit_user(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('Point_of_Sale.db') as conn:
            incoming_data = dict(request.json)

            put_data = {}

            if incoming_data.get("first_name") is not None:
                put_data["first_name"] = incoming_data.get("first_name")
                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user SET first_name =? WHERE user_id=?", (put_data["first_name"], post_id))
                    conn.commit()
                    response['message'] = "Name updated successfully"
                    response['status_code'] = 200
            if incoming_data.get("last_name") is not None:
                put_data['last_name'] = incoming_data.get('last_name')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user SET last_name =? WHERE user_id=?", (put_data["last_name"], post_id))
                    conn.commit()

                    response["content"] = "Last name updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("username") is not None:
                put_data['username'] = incoming_data.get('username')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user SET username =? WHERE user_id=?", (put_data["username"], post_id))
                    conn.commit()

                    response["content"] = "User name updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("password") is not None:
                put_data['password'] = incoming_data.get('password')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user SET password =? WHERE user_id=?", (put_data["password"], post_id))
                    conn.commit()

                    response["content"] = "Password updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("address") is not None:
                put_data['address'] = incoming_data.get('address')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user SET address =? WHERE user_id=?", (put_data["address"], post_id))
                    conn.commit()

                    response["content"] = "Address updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("phone_number") is not None:
                put_data['phone_number'] = incoming_data.get('phone_number')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user SET phone_number =? WHERE user_id=?", (put_data["phone_number"], post_id))
                    conn.commit()

                    response["content"] = "Phone number updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("user_email") is not None:
                put_data['user_email'] = incoming_data.get('user_email')

                with sqlite3.connect('Point_of_Sale.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE user SET user_email =? WHERE user_id=?", (put_data["user_email"], post_id))
                    conn.commit()

                    response["content"] = "email updated successfully"
                    response["status_code"] = 200

    return response


# run the app
if __name__ == '__main__':
    app.run(debug=True)
