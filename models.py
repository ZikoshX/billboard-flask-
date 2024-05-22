from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Manager(db.Model):
    __tablename__ = 'manager'
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
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'
    
class Users(db.Model):
    __tablename__ = 'users'
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

class Orders(db.Model):
    __tablename__ = 'orders'
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
    user_name = db.Column(db.String(255), nullable=False)
    user_lastname = db.Column(db.String(255), nullable=False)
    submitted_date = db.Column(db.DateTime, default=datetime.now)
    payment_status = db.Column(db.String(50), default='unpaid')
    penalty = db.Column(db.Integer, default=0)
    penalty_status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f"<Order(company_name='{self.billboard_info}', start_date='{self.start_date}', end_date='{self.end_date}')>"

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    card_number_encrypted = db.Column(db.String(16))
    cardholder_name = db.Column(db.String(255))
    expiration = db.Column(db.String(5))  # Assuming expiration is stored as 'MM/YY' format
    cvv_encrypted = db.Column(db.String(3))
    amount = db.Column(db.Float) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(255), db.ForeignKey('users.name'), nullable=False)
    user_lastname = db.Column(db.String(255), db.ForeignKey('users.lastname'), nullable=False)

    def __repr__(self):
        return f"<Payment(card_number='{self.card_number}', cardholder_name='{self.cardholder_name}')>"
