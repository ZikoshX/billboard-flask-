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


app=Flask(__name__)


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
    column_display_pk = True  # Display primary keys in the list view
    column_searchable_list = ['name', 'email']   

app.secret_key = secrets.token_hex(16)  # Generate a random 32-character hexadecimal string

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

    # Define the relationship between Manager and Posts
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


# Add Manager and Posts views as before
admin.add_view(ModelView(Manager, db.session))
admin.add_view(ModelView(Posts, db.session))
admin.add_view(ModelView(Users, db.session))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

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
    cursor=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method=='POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
       name=request.form['name']
       lastname=request.form['lastname']
       username=request.form['username']
       password=request.form['password']
       email=request.form['email']
       phone_number=request.form['phone_number']
       print(name)
       print(username)
       print(password)
       print(email)

       _hashed_password=generate_password_hash(password)

       cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
       account=cursor.fetchone()
       print(account)
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
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (name,lastname, username, password, email, phone_number) VALUES (%s,%s,%s,%s,%s,%s)", (name, lastname, username, _hashed_password, email, phone_number))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method=='POST':
            flash('Please fill out the form!')
    return render_template('signup.html')   

@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        # Attempt to authenticate as a manager
        manager = Manager.query.filter_by(username=username).first()
        if manager and check_password_hash(manager.password, password):
            # Authentication successful, set session variables for manager
            session['loggedin'] = True
            session['manager_id'] = manager.id
            session['manager_name'] = manager.name
            flash('Manager login successful!', 'success')
            return redirect(url_for('manager'))  # Redirect to manager profile route

        # Attempt to authenticate as a user
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # Authentication successful, set session variables for user
            session['loggedin'] = True
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('User login successful!', 'success')
            return redirect(url_for('profile'))  # Redirect to user profile route
        
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
   app.run(debug=True, port=5001)
