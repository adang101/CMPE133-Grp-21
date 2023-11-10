from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from datetime import datetime
from flask_login import UserMixin
from flask import url_for
from flask_migrate import Migrate

db = SQLAlchemy()

# Create a database engine
engine = create_engine('sqlite:///Casso_database.db', echo=True)

# User model to store user information
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    biography = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255), default='default.jpg')

    # Constructor
    def __init__(self, id, full_name, username, email, password, biography=None, profile_picture=None):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password = password
        self.biography = biography
        self.profile_picture = profile_picture
    
    def get_id(self): 
        return super().get_id()    
    def get(user_id):
        return User.query.get(int(user_id))    
    def is_authenticated(self):
        return True    
    def is_active(self):
        return True   
    def is_anonymous(self):
        return False

    # User Relationships with other models
    posts = db.relationship('Post', backref='user', lazy=True) # One to many

    commission_requests_sent = db.relationship('CommissionRequest', 
        foreign_keys='CommissionRequest.sender_id',
        backref='sender', lazy='dynamic') # One to many
    commission_requests_received = db.relationship('CommissionRequest', 
        foreign_keys='CommissionRequest.receiver_id',
        backref='receiver', lazy='dynamic') # One to many
    
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', 
        backref='sender', lazy='dynamic') # One to many
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', 
        backref='receiver', lazy='dynamic') # One to many
    
    likes = db.relationship('Like', backref='user', lazy='dynamic') # One to many

    followers = db.relationship('Follower', foreign_keys='Follower.followed_id', 
        backref='followed', lazy='dynamic') # One to many
    following = db.relationship('Follower', foreign_keys='Follower.follower_id', 
        backref='follower', lazy='dynamic') # One to many
    
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

# Post model to store user posts
# (Each user can have multiple posts)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    def image_url(self):
        return url_for('static', filename=f'images/userPosts/{self.image}')
    
    # Post Relationships with other models
    likes = db.relationship('Like', backref='post', lazy='dynamic') # One to many

# Commission model to store user commissions
# (Each user can have multiple commissions)
class CommissionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    # Additional fields for commission details (add more as needed)
    commission_details = db.Column(db.String(255))
    payment_status = db.Column(db.String(50), default='Pending')

# Message model to store user messages
# (Each user can have multiple messages / open chats)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    read = db.Column(db.Boolean, default=False)  # Added for read/unread status
    message_type = db.Column(db.String(50))  # Added for categorizing messages

    def __init__(self, sender_id, receiver_id, content, message_type=None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.message_type = message_type

# Follower model to store user followers and following
# Many-to-many relationship with User model (Each user can follow multiple users and be followed by multiple users)
class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, follower_id, followed_id):
        self.follower_id = follower_id
        self.followed_id = followed_id

# Comment model to store user comments on posts
# Many-to-one relationship with Post model (Each post can have multiple comments)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, text, user_id, post_id):
        self.text = text
        self.user_id = user_id
        self.post_id = post_id

# Like model to store user likes on posts
# Many-to-one relationship with Post and User models (Each post can have multiple likes and each user can like multiple posts)
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer)
    notification_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)

    # Additional fields to store specific information about the notification
    # For example, the post_id for like notifications, message_id for message notifications, etc.
    related_id = db.Column(db.Integer)

    def __init__(self, user_id, sender_id, notification_type, related_id):
        self.user_id = user_id
        self.sender_id = sender_id
        self.notification_type = notification_type
        self.related_id = related_id

# Create all tables in the engine. This is equivalent to "Create Table"
#metadata = MetaData()

#users = Table('users', metadata,
#    Column('id', Integer, primary_key=True),
#    Column('username', String(80), unique=True, nullable=False),
#    Column('email', String(120), unique=True, nullable=False),
#    Column('password', String(60), nullable=False),
#    Column('biography', String(255)),
#    Column('gender', String(10))
#)

#metadata.create_all(engine)