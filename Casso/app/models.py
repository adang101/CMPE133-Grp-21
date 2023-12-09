from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import EmailType
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from datetime import datetime
from flask_login import UserMixin, current_user
from flask import url_for, session
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
engine = create_engine('sqlite:///Casso_database.db', echo=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(EmailType, unique=True, nullable=False)
    password = db.Column(db.String(60))
    biography = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255), default='default.jpg')

    def __init__(self, full_name, username, email, password, biography=None, profile_picture=None):
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password = password
        self.biography = biography
        self.profile_picture = profile_picture

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
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
    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
            db.session.commit()
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()
    
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')

    commission_requests_sent = db.relationship('CommissionRequest',
        foreign_keys='CommissionRequest.sender_id',
        back_populates='sender',
        lazy='dynamic',
        cascade='all, delete-orphan')
    commission_requests_received = db.relationship('CommissionRequest',
        foreign_keys='CommissionRequest.receiver_id',
        back_populates='receiver',
        lazy='dynamic',
        cascade='all, delete-orphan')
    
    payments_sent = db.relationship('Payment',
        foreign_keys='Payment.payer_id',
        back_populates='payer',
        lazy='dynamic',
        cascade='all, delete-orphan')
    payments_received = db.relationship('Payment',
        foreign_keys='Payment.payee_id',
        back_populates='payee',
        lazy='dynamic',
        cascade='all, delete-orphan')
    
    messages_sent = db.relationship('Message', 
        foreign_keys='Message.sender_id', 
        backref='sent_messages', 
        lazy='dynamic', 
        overlaps="sent_messages",
        cascade='all, delete-orphan')
    messages_received = db.relationship('Message', 
        foreign_keys='Message.receiver_id', 
        backref='received_messages', 
        lazy='dynamic',
        overlaps="received_messages",
        cascade='all, delete-orphan')
    
    chat_sessions_as_user1 = db.relationship('ChatSession',
        foreign_keys='ChatSession.user1_id',
        backref='user1',
        lazy='dynamic',
        cascade='all, delete-orphan')
    chat_sessions_as_user2 = db.relationship('ChatSession',
        foreign_keys='ChatSession.user2_id',
        backref='user2',
        lazy='dynamic',
        cascade='all, delete-orphan')
    
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', 
        backref='followed', 
        lazy='dynamic', 
        cascade='all, delete-orphan')
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', 
        backref='follower', 
        lazy='dynamic', 
        cascade='all, delete-orphan')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    def image_url(self):
        return url_for('static', filename=f'images/userPosts/{self.image}')

class CommissionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    artwork_dimensions = db.Column(db.String(50))
    desired_budget = db.Column(db.String(50))
    commission_details = db.Column(db.String(255))
    payment_status = db.Column(db.String(50), default='Pending')
    
    payment = db.relationship('Payment', back_populates='commission_request', uselist=False)
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='commission_requests_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='commission_requests_received')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_owner_name = db.Column(db.String(255), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    expiry_date = db.Column(db.String(4), nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commission_request_id = db.Column(db.Integer, db.ForeignKey('commission_request.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    payer = db.relationship('User', foreign_keys=[payer_id], back_populates='payments_sent')
    payee = db.relationship('User', foreign_keys=[payee_id], back_populates='payments_received')
    commission_request = db.relationship('CommissionRequest', back_populates='payment')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    chat_session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'))

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages', overlaps="sent_messages")
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages', overlaps="sent_messages")
    chat_session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'))
    chat_session = db.relationship('ChatSession', back_populates='messages')

    def __init__(self, sender_id, receiver_id, content, chat_session_id, file_path=None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.file_path = file_path
        self.chat_session_id = chat_session_id

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    messages = db.relationship('Message', back_populates='chat_session', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, user1_id, user2_id):
        self.user1_id, self.user2_id = (user1_id, user2_id) if user1_id == current_user.id else (user2_id, user1_id)

    def get_messages(self):
        return Message.query.filter_by(chat_session_id=self.id).order_by(Message.created_at.asc())

class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, follower_id, followed_id):
        self.follower_id = follower_id
        self.followed_id = followed_id

    @classmethod
    def is_following(cls, follower_id, followed_id):
        return cls.query.filter_by(follower_id=follower_id, followed_id=followed_id).first() is not None

    def toggle_follow(self):
        db.session.delete(self) if self else db.session.add(self)
        db.session.commit()

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, follower_id, followed_id):
        self.follower_id = follower_id
        self.followed_id = followed_id

'''class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, text, user_id, post_id):
        self.text = text
        self.user_id = user_id
        self.post_id = post_id'''

'''class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id'''

'''class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer)
    notification_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)

    related_id = db.Column(db.Integer)

    def __init__(self, user_id, sender_id, notification_type, related_id):
        self.user_id = user_id
        self.sender_id = sender_id
        self.notification_type = notification_type
        self.related_id = related_id'''

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