from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# Create a database engine
engine = create_engine('sqlite:///Casso_database.db', echo=True)

# User model to store user information
# stores user information such as username, email, and hashed password.
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

    # Required for administrative interface session will be managed by Flask-Login. You can use
    #   current_user to check if a user is logged in, 
    #   login_required decorator to restrict access / protect views that should only be 
    #       accessible by logged in users,
    #   logout_user to log users out when needed.
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

    # Relationship with posts
    posts = db.relationship('Post', backref='user', lazy=True)

    # Relationships to followers and following
    followers = db.relationship('Follower', foreign_keys='Follower.followed_id', 
                                backref='followed', lazy='dynamic')
    following = db.relationship('Follower', foreign_keys='Follower.follower_id', 
                                backref='follower', lazy='dynamic')

    # Likes relationship
    likes = db.relationship('Like', backref=db.backref('user', lazy='joined'), lazy='dynamic')

# Post model to store user posts
# One-to-many relationship with User model (Each user can have multiple posts)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Comments relationship
    comments = db.relationship('Comment', backref=db.backref('post', lazy='joined'), lazy='dynamic')

    # Likes relationship
    likes = db.relationship('Like', backref=db.backref('post', lazy='joined'), lazy='dynamic')

    def __init__(self, image, caption, user_id):
        self.image = image
        self.caption = caption
        self.user_id = user_id

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

# Create all tables in the engine. This is equivalent to "Create Table"
metadata = MetaData()

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(80), unique=True, nullable=False),
    Column('email', String(120), unique=True, nullable=False),
    Column('password', String(60), nullable=False),
    Column('biography', String(255)),
    Column('gender', String(10))
)

metadata.create_all(engine)