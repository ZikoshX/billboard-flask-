import inspect
import pathlib
from flask import Flask, render_template, request, flash, url_for, session, redirect, abort, session
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from google_auth_oauthlib.flow import Flow
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_mail import Mail, Message
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, BaseView
from werkzeug.utils import secure_filename
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from sqlalchemy import desc
from flask import session, current_app
import traceback

app=Flask(__name__)

UPLOAD_FOLDER = 'path/to/upload/folder'

# Check if the upload folder exists, and create it if it doesn't
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Update the Flask application configuration with the upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/add/<int:num1>/<int:num2>')
def add(num1, num2):
    return str(num1 + num2)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mashrapzere44@gmail.com'
app.config['MAIL_PASSWORD'] = 'cdha zmdd hhlh tjvq'

mail = Mail(app)
admin = Admin(app)
class ManagerView(ModelView):
    column_display_pk = True 
    column_searchable_list = ['name', 'email']   

app.secret_key = secrets.token_hex(16)  

GOOGLE_CLIENT_ID='187314309127-bo52fulqluaqls64aefmcm453k3mrg5p.apps.googleusercontent.com'
client_secrets_file=os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/google-login"
)

DB_HOST='localhost'
DB_NAME='sampledb'
DB_USER='postgres'
DB_PASS='13579'

conn=psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(20))
    posts = db.relationship('Posts', backref='manager', lazy='dynamic')

    def __repr__(self):
        return f'<Manager {self.username}>'

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    def __repr__(self):
        return f'<Post {self.title}>'
    
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(20))
    posts = db.relationship('Posts', backref='users', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return redirect('/home')

    def _menu(self):
        menu = super()._menu()
        menu.append(('home', 'Home'))
        return menu

    def is_visible(self):
        return False
class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    billboard_info = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    region = db.Column(db.String(255), nullable=False)
    display_type = db.Column(db.String(255), nullable=False)
    surface_type = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)  # Corrected to String
    user_lastname = db.Column(db.String(255), nullable=False)  # Corrected to String
    submitted_date = db.Column(db.DateTime, default=datetime.now)
    payment_status = db.Column(db.String(50), default='unpaid')
    penalty = db.Column(db.Integer, default=0)
    penalty_status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f"<Order(company_name='{self.billboard_info}', start_date='{self.start_date}', end_date='{self.end_date}')>"

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number_encrypted = db.Column(db.String(16))
    cardholder_name = db.Column(db.String(255))
    expiration = db.Column(db.String(5))  # Assuming expiration is stored as 'MM/YY' format
    cvv_encrypted = db.Column(db.String(3))
    amount = db.Column(db.Float) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(255), db.ForeignKey('users.name'), nullable=False)  # Corrected to String
    user_lastname = db.Column(db.String(255), db.ForeignKey('users.lastname'), nullable=False)  # Corrected to String

    def __repr__(self):
        return f"<Payment(card_number='{self.card_number}', cardholder_name='{self.cardholder_name}')>"    
admin.add_view(ModelView(Manager, db.session))
admin.add_view(ModelView(Posts, db.session))
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Orders, db.session))
admin.add_view(ModelView(Payment, db.session))


@app.route('/order_history')
def order_history():
    user_id = session.get('user_id')  # Assuming you store the user's ID in the session
    if user_id is None:
        # Handle the case where the user is not logged in or the session is expired
        return "User not logged in", 403

    # Retrieve orders belonging to the current user
    orders = Orders.query.filter_by(user_id=user_id).all()
    active_page = 'order'
    return render_template('order_history.html', orders=orders,active_page=active_page)

@app.route('/penaltymanager', methods=['GET', 'POST'])
def penaltymanager():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        action = request.form.get('action')

        if action == 'acceptpayment':
                accept_penalty(order_id)
        elif action == 'rejectpayment':
                reject_penalty(order_id)

        return redirect(url_for('penaltymanager'))

    orders = Orders.query.filter(Orders.penalty != 0).order_by(Orders.submitted_date).all()
    grouped_orders = {
        date: list(items) for date, items in groupby(orders, key=lambda order: order.submitted_date.date())
    }

    active_page = 'penaltymanager'
    return render_template('penaltymanager.html', grouped_orders=grouped_orders, active_page=active_page)

def accept_penalty(order_id):
    order = Orders.query.get(order_id)
    if order:
        try:
            order.status = 'accepted' 
            order.penalty_status = 'accepted'  # Update penalty status to 'accepted'
            db.session.commit()
            print(f"Order ID: {order_id}, Status: {order.status}, Payment Status: {order.penalty_status}")
        except Exception as e:
            print(f"Error updating penalty status for Order ID {order_id}: {str(e)}")
    else:
        print(f"Order ID {order_id} not found.")

def reject_penalty(order_id):
    order = Orders.query.get(order_id)
    if order:
        order.status = 'rejected' 
        order.penalty_status = 'rejected'  # Assuming penalty remains pending upon rejection
        db.session.commit()
        print(f"Order ID {order_id} has been rejected.")
    else:
        print(f"Order ID {order_id} not found.")

@app.route('/status_order', methods=['GET'])
def status_order():
    user_name = session.get('name')
    user_lastname = session.get('lastname')

    user_orders = Orders.query.filter(
        Orders.user_name == user_name,
        Orders.user_lastname == user_lastname,
        Orders.payment_status == 'paid'
    ).order_by(desc(Orders.submitted_date)).all()

    return render_template('status_order.html', user_orders=user_orders)

@app.route('/orders', methods=['POST', 'GET'])
def orders():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        action = request.form.get('action')

        if action == 'accept':
            accept_order(order_id)
        elif action == 'reject':
            reject_order(order_id)

        return redirect(url_for('orders'))

    orders = Orders.query.order_by(Orders.submitted_date).all()
    orders.sort(key=lambda order: order.submitted_date.date())

    grouped_orders = {
        date: list(items) for date, items in groupby(orders, key=lambda order: order.submitted_date.date())
    }

    active_page = 'orders'
    return render_template('orders.html', orders=orders, grouped_orders=grouped_orders, active_page=active_page)

def accept_order(order_id):
    order = Orders.query.get(order_id)
    if order:
        order.status = 'accepted'  # Update the status column
        order.payment_status = 'paid'  # Update the payment status
        db.session.commit()
        print(f"Order ID: {order_id}, Status: {order.status}, Payment Status: {order.payment_status}")
        return True
    else:
        print("Order not found")
        return False

def reject_order(order_id):
    order = Orders.query.get(order_id)
    if order:
        order.status = 'rejected'  # Update the status column
        order.payment_status = 'rejected'
        db.session.commit()
        print(f"Order ID: {order_id}, Status: {order.payment_status}")
    else:
        print("Order not found")


@app.route('/accept_payment/<int:order_id>', methods=['GET'])
def accept_payment(order_id):
    order = Orders.query.get(order_id)
    if order:
        order.payment_status = 'accepted'
        db.session.commit()
        flash('Payment accepted successfully.', 'success')
    else:
        flash('Order not found.', 'error')
    return redirect(url_for('orders'))

@app.route('/reject_payment/<int:order_id>', methods=['GET'])
def reject_payment(order_id):
    order = Orders.query.get(order_id)
    if order:
        order.payment_status = 'rejected'
        db.session.commit()
        flash('Payment rejected successfully.', 'success')
    else:
        flash('Order not found.', 'error')
    return redirect(url_for('orders'))

@app.route('/home')
def home():
    active_page = 'home'
    return render_template('home.html', active_page=active_page)

@app.route('/penalty', methods=['GET'])
def penalty():
    user_name = session.get('name')
    user_lastname = session.get('lastname')
    changed_order_id = session.get('changed_order_id')
    changed_fields = session.get('changed_fields')

    app.logger.info(f"Changed order ID: {changed_order_id}")
    app.logger.info(f"Changed fields: {changed_fields}")

    # Assuming the username is stored in the 'username' column of the Orders table
    orders_with_penalty = Orders.query.filter(Orders.user_name == user_name, Orders.penalty != 0).all()

    active_page = 'penalty'

    return render_template('penalty.html', name=user_name, orders_group=orders_with_penalty, lastname=user_lastname, active_page=active_page)
@app.route('/schedule')
def schedule():
    active_page='schedule'
    return render_template('schedule.html', active_page=active_page)

@app.route('/loginclient', methods=['GET', 'POST'])
def loginclient():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['lastname'] = user.lastname
            flash('Login successful!', 'success')
            return redirect(url_for('loginclient'))  # Redirect to home page after successful login
        else:
            flash('Invalid username or password', 'danger')
    active_page='loginclient'
    # GET request or invalid login attempt, render login form
    return render_template('loginclient.html', active_page=active_page)

@app.route('/loginmanager', methods=['GET', 'POST'])
def loginmanager():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Manager.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['lastname'] = user.lastname
            flash('Login successful!', 'success')
            return redirect(url_for('loginmanager'))  # Redirect to home page after successful login
        else:
            flash('Invalid username or password', 'danger')
    active_page='loginmanager'
    # GET request or invalid login attempt, render login form
    return render_template('loginmanager.html', active_page=active_page)

@app.route('/chat')
def chat():
    active_page = 'chat'
    return render_template('chat.html', active_page=active_page)

@app.route('/manager_settings', methods=['POST','GET'])
def manager_settings():
    active_page='manager_settings'
    return render_template('manager_settings.html', active_page=active_page)

@app.route('/chatmanager')
def chatmanager():
    active_page = 'chatmanager'
    return render_template('chatmanager.html', active_page=active_page)

@app.route('/calendar')
def calendar():
    active_page='calendar'
    return render_template('calendar.html', active_page=active_page)


@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    active_page='settings'
    return render_template('settings.html', active_page=active_page)

@app.route('/profile', methods=['POST','GET'])
def profile():
    order_details = session.get('order_details')
    name = session.get('name')
    surname = session.get('lastname')
    active_page='profile'
    
    return render_template('profile.html', name=name, surname=surname, active_page=active_page)
   

@app.route('/next_order')
def next_order():
    return render_template('next_order.html')

@app.route('/changed_order/<int:order_id>', methods=['POST', 'GET'])
def changed_order(order_id):
    # Fetch the order details from the database
    name = session.get('name')
    surname = session.get('lastname')
    order = Orders.query.get(order_id)

    if request.method == 'POST':
        # Retrieve form data
        company_name = request.form['company-name']
        billboard_info = request.form['billboard-info']
        start_date = request.form['Start']
        end_date = request.form['End']
        region = request.form['city']
        display_type = request.form['display']
        surface_type = request.form['surface']

        # Check if any fields have changed
        changed_fields = []
        if order.company_name != company_name:
            changed_fields.append("Company Name")
        if order.billboard_info != billboard_info:
            changed_fields.append("Billboard Info")
        if order.start_date != start_date:
            changed_fields.append("Start Date")
        if order.end_date != end_date:
            changed_fields.append("End Date")
        if order.region != region:
            changed_fields.append("Region")
        if order.display_type != display_type:
            changed_fields.append("Display Type")
        if order.surface_type != surface_type:
            changed_fields.append("Surface Type")

        # Update the order information in the database
        order.company_name = company_name
        order.billboard_info = billboard_info
        order.start_date = start_date
        order.end_date = end_date
        order.region = region
        order.display_type = display_type
        order.surface_type = surface_type

        # Commit changes to the database
        db.session.commit()

        if changed_fields:
            # Store the changed order ID and changed fields in the session
            session['changed_order_id'] = order_id
            session['changed_fields'] = changed_fields
            # Calculate the penalty amount
            penalty_amount = calculate_penalty_amount(changed_fields)
            order.penalty=penalty_amount
            db.session.commit()
            # Redirect to the penalty page
            return redirect(url_for('penalty', order_id=order_id, penalty_amount=penalty_amount))


        return redirect(url_for('orderhistory'))

    active_page = 'change'
    # Pass the order object to the template
    return render_template('changed_order.html',  name=name, surname=surname, order=order, order_id=order_id, surface=order.surface_type, display=order.display_type, price=order.price, active_page=active_page)

@app.route('/payment/<int:order_id>', methods=['POST', 'GET'])
def payment(order_id):
    order = Orders.query.get(order_id)
    if not order:
        return "Order not found", 404

    if request.method == 'POST':
        try:
            # Logic to update order status to indicate payment
            order.paid = True  # Assuming you have a 'paid' attribute in your Orders model
            db.session.commit()  # Assuming you're using SQLAlchemy

            # Logic to send email confirmation
            user = Users.query.get(order.user_id)
            if user:
                send_confirmation_email(user.email, order_id, order.price)
            else:
                flash("User associated with the order not found", 'danger')

            # Redirect to the confirmation page after payment
            return redirect(url_for('conf', order_id=order_id))
        except Exception as e:
            db.session.rollback()  # Rollback the transaction in case of an error
            flash("An error occurred while processing your payment", 'danger')
            # Log the exception for debugging purposes
            print(e)

    # Assuming you have the following variables available in the template
    name = order.user_name
    price = int(order.price)
    active_page = 'payment'

    return render_template('payment.html', order=order, name=name, price=price, active_page=active_page)

def send_confirmation_email(email, order_id, price):
    token = str(uuid.uuid4())
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        # Check if the email exists in the database
        result = cursor.execute('SELECT * FROM users WHERE  email=%s', [email])
        account = cursor.fetchone()
        if account:
            msg = Message(subject="Order Confirmation and Receipt", sender="mashrapzere44@gmail.com", recipients=[email])
            msg.body = render_template('sentreceipt.html', token=token, email=email, order_id=order_id, price=price)
            mail.send(msg)
            cursor.execute("UPDATE users SET token=%s WHERE email=%s", [token, email])
            conn.commit()
            flash("Email sent successfully!", 'success')
        else:
            flash("Email does not exist in the database", 'danger')
    except Exception as e:
        conn.rollback()  # Rollback the transaction in case of an error
        flash("An error occurred while sending the email", 'danger')
        # Log the exception for debugging purposes
        print(e)
    finally:
        cursor.close()
@app.route('/conf/<int:order_id>', methods=['GET', 'POST'])
def conf(order_id):
    
    # Logic to retrieve order details from the database
    order = Orders.query.get(order_id)

    if not order:
        # Handle case where order is not found
        return "Order not found", 404

    # Pass the order details to the template
    active_page = 'conf'
    return render_template('conf.html', order=order, active_page=active_page)


@app.route('/orderhistory', methods=['POST', 'GET'])
def orderhistory():
    user_name = session.get('name')
    user_lastname = session.get('lastname')

    user_orders = Orders.query.filter(Orders.user_name == user_name, Orders.user_lastname == user_lastname).order_by(desc(Orders.submitted_date)).all()

    grouped_orders = {}
    for date, orders_group in groupby(user_orders, key=lambda order: order.submitted_date.date()):
        grouped_orders[date] = list(orders_group)

    if request.method == 'POST':
        order_id = request.form.get('order_id')
        updated_billboard_info = request.form.get('billboard_info')
        updated_pdf_path = request.form.get('pdf_path')
        updated_start_date = request.form.get('start_date')
        updated_end_date = request.form.get('end_date')
        updated_region = request.form.get('region')
        updated_display_type = request.form.get('display_type')
        updated_surface_type = request.form.get('surface_type')

        order = Orders.query.get_or_404(order_id)

        changed_fields = []

        if order.billboard_info != updated_billboard_info:
            order.billboard_info = updated_billboard_info
            changed_fields.append("Billboard Info")
        if order.start_date != updated_start_date:
            order.start_date = updated_start_date
            changed_fields.append("Start Date")
        if order.end_date != updated_end_date:
            order.end_date = updated_end_date
            changed_fields.append("End Date")
        if order.region != updated_region:
            order.region = updated_region
            changed_fields.append("Region")
        if order.display_type != updated_display_type:
            order.display_type = updated_display_type
            changed_fields.append("Display Type")
        if order.surface_type != updated_surface_type:
            order.surface_type = updated_surface_type
            changed_fields.append("Surface Type")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of error
            print(f"Error committing changes to the database: {e}")

        print("Changed fields:", changed_fields)
        penalty_amount = calculate_penalty_amount(changed_fields)
        order.penalty = penalty_amount
        db.session.commit()
        return render_template('orderhistory.html', 
                               grouped_orders=grouped_orders, 
                               active_page='orderhistory', 
                               updated_order=order, 
                               penalty_amount=penalty_amount)

    return render_template('orderhistory.html', grouped_orders=grouped_orders, active_page='orderhistory')

def calculate_penalty_amount(changed_fields):
    penalty_amount = 0

    for field in changed_fields:
        if field == "Start Date" or field == "End Date":
            penalty_amount += 30000
        elif field == "Region":
            penalty_amount += 20000
        elif field == "Display Type" or field == "Surface Type":
            penalty_amount += 15000

    return penalty_amount

@app.route('/dashboardmanager', methods=['POST','GET'])
def dashboardmanager():
    name = session.get('name')
    surname = session.get('lastname')
    phone_number = session.get('phone_number')
    email = session.get('email')
    active_page = 'dashboardmanager'
    # Pass the variables to the template rendering function
    return render_template('dashboardmanager.html', name=name, surname=surname, phone_number=phone_number, email=email,active_page=active_page)



@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    # Assuming 'name', 'surname', 'phone_number', and 'email' are stored in session
    
    name = session.get('name')
    username = session.get('username') 
    surname = session.get('lastname')
    phone_number = session.get('phone_number')
    email = session.get('email')

    # Debug output
    current_app.logger.debug(f"Name: {name}")
    current_app.logger.debug(f"Username: {username}")
    current_app.logger.debug(f"Surname: {surname}")
    current_app.logger.debug(f"Phone Number: {phone_number}")
    current_app.logger.debug(f"Email: {email}")

    # Pass the variables to the template rendering function
    return render_template('dashboard.html', name=name, username=username, surname=surname, phone_number=phone_number, email=email, active_page='dashboard')

@app.route('/edit_profile', methods=['POST','GET'])
def edit_profile():
    # Retrieve session variables
    name = session.get('name')
    username = session.get('username')
    surname = session.get('lastname')
    phone_number = session.get('phone_number')
    email = session.get('email')
      # Assuming 'username' is stored in session

    # Pass the session variables to the template rendering function
    return render_template('edit_profile.html', name=name, username=username, surname=surname, phone_number=phone_number, email=email)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            surname = request.form.get('surname')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            
            # Update user information in the database
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET name = %s, lastname = %s, phone_number = %s, email=%s
                    WHERE username = %s;
                """, (name, surname, phone_number,email, session['username']))  # Use username as the condition
                conn.commit()

            # Update session variables with form data
            session['name'] = name
            #session['username'] = username
            session['lastname'] = surname
            session['phone_number'] = phone_number
            session['email'] = email

            return redirect(url_for('dashboard'))
        except Exception as e:
            # Print or log the exception to debug
            print(e)
            flash("An error occurred while updating the profile.", 'error')
            return redirect(url_for('edit_profile'))

@app.route('/submit_order', methods=['POST'])
def submit_order():
    if request.method == 'POST':
        # Retrieve user information from the session
        user_id = session.get('user_id')
        user_name = session.get('name')
        user_lastname = session.get('lastname')

        user = Users.query.filter_by(name=user_name, lastname=user_lastname).first()
        if not user:
            return "User not found", 404
        
        # Retrieve the uploaded PDF file
        pdf_file = request.files['pdf-format']
        if pdf_file:
            filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdf_path = filename
        else:
            pdf_path = None

        # Retrieve order information from the form
        company_name = request.form['company-name']
        billboard_info = request.form['billboard-info']
        region = request.form['city'] 
        display_type = request.form['display']
        surface_type = request.form['surface']
        start_date = request.form['Start']
        end_date = request.form['End']
        price = request.form['total-price']
        # Create a dictionary representation of the order attributes
        order = Orders(
            user_id=user_id,
            user_name=user_name,
            user_lastname=user_lastname,
            company_name=company_name,
            billboard_info=billboard_info,
            pdf_path=pdf_path,
            region=region,
            display_type=display_type,
            surface_type=surface_type,
            start_date=start_date,
            end_date=end_date,
            price=price 
        )

        # Store the order details in the session
        #order = Orders(**order_details)
        #order.calculate_price()  # Assuming calculate_price method exists in the Orders class
        #total_price = order.price
        #order_details['total_price'] = total_price
        db.session.add(order)
        db.session.commit()

        # Redirect to the payment page
        return redirect(url_for('orderhistory'))

    # If the request method is not POST, redirect to some other page
    return redirect(url_for('profile'))

@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    if request.method == 'POST':
        # Retrieve user information from the session
        user_id = session.get('user_id')
        user_name = session.get('name')
        user_lastname = session.get('lastname')

        # Retrieve payment information from the form
        card_number_encrypted = request.form.get('card_number')
        cardholder_name = request.form.get('cardholder_name')
        expiration = request.form.get('expiration')
        cvv_encrypted = request.form.get('cvv')
        # Create payment instance and add to database
        payment = Payment(
            user_id=user_id,
            user_name=user_name,
            user_lastname=user_lastname,
            card_number_encrypted=card_number_encrypted,
            cardholder_name=cardholder_name,
            expiration=expiration,
            cvv_encrypted=cvv_encrypted,
           
        )
        db.session.add(payment)

        # Commit payment information to the database
        db.session.commit()

        # Retrieve the order details from the session
        order_details = session.get('order_details')

        # If order details exist in the session, save the order in the database
        if order_details:
            order = Orders(**order_details)
            db.session.add(order)
            db.session.commit()

        # Redirect to the order history page
        return redirect(url_for('orderhistory'))

    # If the request method is not POST, redirect to some other page
    return redirect(url_for('orderhistory'))
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper
@app.route('/google-login')
def google_login():
    # Generate the URL for the Google login callback
    google_login_url = url_for('google_callback', _external=True)
    return render_template('home.html', google_login_url=google_login_url)

@app.route('/callback')
def callback():
    # Fetch the authorization response from Google
    authorization_response = request.url

    # Fetch the token
    flow.fetch_token(authorization_response=authorization_response)

    # Get user info from Google
    google_id_token = flow.credentials.id_token
    google_user_info = id_token.verify_oauth2_token(google_id_token, requests.Request(), GOOGLE_CLIENT_ID)

    # Check if the user already exists in your database
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email=%s', (google_user_info['email'],))
    account = cursor.fetchone()

    if account:
        # User exists, log them in
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return redirect(url_for('profile'))
    else:
        # User doesn't exist, you can register them if needed
        flash('User does not exist. You may need to register.')
        return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            name = request.form['name']
            lastname = request.form['lastname']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone_number = request.form['phone_number']

            _hashed_password = generate_password_hash(password)

            cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
            account = cursor.fetchone()
            if account:
                flash('Account already exists!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash('Username must contain only characters and numbers!')
            elif not re.match(r'^(?=.*[a-z])(?=.*\d).{8,}$', password):
                flash('Password must be at least 8 characters long and contain at least one number and one lowercase letter!')
            elif not username or not password or not email:
                flash('Please fill out the form!')
            elif not phone_number.isdigit():
                flash('Phone number must contain only digits!')
            else:
                # Account doesn't exist and the form data is valid, now insert new account into users table
                cursor.execute("INSERT INTO users (name,lastname, username, password, email, phone_number) VALUES (%s,%s,%s,%s,%s,%s)", (name, lastname, username, _hashed_password, email, phone_number))
                conn.commit()
                flash('You have successfully registered!')
        elif request.method == 'POST':
            flash('Please fill out the form!')
    except Exception as e:
        conn.rollback()
        flash('An error occurred while processing your request. Please try again later.')
        # Log the exception details for debugging purposes
        traceback.print_exc()  # Print the traceback to the console
    finally:
        cursor.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        # Attempt to authenticate as a manager
        manager = Manager.query.filter_by(username=username).first()
        if manager:
            # Authentication successful, set session variables for manager
            session['loggedin'] = True
            session['manager_id'] = manager.id
            session['username'] = manager.username
            session['name'] = manager.name
            session['lastname'] = manager.lastname
            session['phone_number'] = manager.phone_number
            session['email'] = manager.email
            flash('Manager login successful!', 'success')
            return redirect(url_for('loginmanager'))  # Redirect to manager profile route

        # Attempt to authenticate as a user
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # Authentication successful, set session variables for user
            session['loggedin'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['name'] = user.name
            session['lastname'] = user.lastname
            session['phone_number'] = user.phone_number
            session['email'] = user.email
            flash('User login successful!', 'success')
            return redirect(url_for('loginclient'))  # Redirect to user profile route
        
        # If authentication fails for both manager and user
        flash('Incorrect username or password', 'danger')

    elif request.method == 'GET':
        # Display login form with Google login link
        google_login_url, _ = flow.authorization_url()
        return render_template('login.html', google_login_url=google_login_url)

    return render_template('login.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        # Retrieve username from session or form data
        if 'username' in session:
            username = session['username']
        else:
            username = request.form.get('username')

        # Process the password change request
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('change_password'))

        # Update the password in the database for the specified user
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password=%s WHERE username=%s", (hashed_password, username))
        conn.commit()

        # Clear session to invalidate existing login
        session.clear()

        flash('Your password has been changed successfully. Please log in again.')
        return redirect(url_for('login'))  # Redirect to login page after changing password
    else:
        # Render the change password form
        return render_template('change_password.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if 'login' in session:
        return redirect('/')
    if request.method == 'POST':
        email = request.form['email']
        #username = request.form['username']  
        token = str(uuid.uuid4())
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Check if the username exists in the database
        result = cursor.execute('SELECT * FROM users WHERE  email=%s', [email])
        account = cursor.fetchone()
        if account:
            msg=Message(subject="Forgot password request", sender="mashrapzere44@gmail.com", recipients=[email])
            msg.body = render_template('sent.html', token=token, account=account)
            mail.send(msg)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("UPDATE users SET token=%s WHERE email=%s", [token,email])
            conn.commit()
            cursor.close()
            flash("Email already sent to your email", 'success')
            return redirect(url_for('forgot_password'))
        else:
            flash("Email do not match", 'danger')
            
        #if account:
            # Redirect to change_password route only if the email and username combination is correct
            #return redirect(url_for('change_password'))
        #else:
            #flash('User with this username and email combination does not exist.')

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'login' in session:
        return redirect('/')
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        #username = request.form['username']  
        token1 = str(uuid.uuid4())
        if password!=confirm_password:
           flash("Passwords do not match", 'danger')
           return redirect(url_for('reset_password'))
        password=generate_password_hash(confirm_password)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        result = cursor.execute('SELECT * FROM users WHERE  token=%s', [token])
        account = cursor.fetchone()
        if account:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("UPDATE users SET token=%s, password=%s WHERE token=%s", [token1,password,token])
            conn.commit()
            cursor.close()
            flash("Your password successfully updated", 'success')
            return redirect(url_for('login'))
        else:
            flash("Your token is invalid", 'danger')

    return render_template('reset_password.html')

def send_reset_email(email, reset_token):
    # Create a password reset email message
    msg = Message('Password Reset Request',
                  sender='your_email@gmail.com',
                  recipients=[email])
    msg.body = 'To reset your password, click the following link: {}'.format(url_for('reset_password', token=reset_token, _external=True))

    # Send the email
    mail.send(msg)




if __name__=='__main__':
   app.run(debug=True, port='5002')
