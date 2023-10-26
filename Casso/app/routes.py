from flask import render_template, Blueprint, request, redirect, url_for, flash
from .models import User, db
import re

bp = Blueprint('main', __name__)

# Define views (routes) for your application

# Path to landing page (index.html)
@bp.route('/')
def index():
    return render_template('index.html')

# Path to login page (login.html)
@bp.route('/login')
def login():
    return render_template('login.html')

# Path to sign up page (sign-up.html)
@bp.route('/sign-up')
def sign_up():
    return render_template('sign-up.html')

# Handle sign up form submission
@bp.route('/sign-up-request', methods=['POST'])
def sign_up_form():
    if request.method == 'POST':
        # Query the database to get the total number of users
        total_users = User.query.count()
        # Create a new user object ID
        new_id = total_users + 1

        new_full_name = request.form['full_name']
        new_user = request.form['username']
        new_email = request.form['email']
        new_password = request.form['password']
        check_password = request.form['check_password']

        # Check if the username or email already exists in the database
        verify_username = User.query.filter_by(username=new_user).first()
        if verify_username is not None:
            flash('Username already exists. Please try again.')
            return redirect(url_for('/sign-up'))

        verify_email = User.query.filter_by(email=new_email).first()
        if verify_email is not None:
            flash('Email already exists. Please try again.')
            return redirect(url_for('/sign-up'))

        verify_full_name = User.query.filter_by(full_name=new_full_name).first()
        if verify_full_name is not None:
            flash('Full name already exists. Please try again.')
            return redirect(url_for('/sign-up'))

        # Check if email is in a valid format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", request.form['email']):
            flash('Email is not in a valid format. Please enter a valid email address.')
            return redirect(url_for('/sign-up'))
        
        # Check if password and check password fields match
        if new_password != check_password:
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('/sign-up'))
        
        # Create a new User object using form data and add to database
        new_user = User(id=new_id, 
            full_name = request.form['full-name'],
            username = request.form['username'],
            email = request.form['email'],
            password = request.form['password'])
        
        # Add new user to database
        db.session.add(new_user)
        db.session.commit()

        # Check if the new user was added to the database
        verify_user = User.query.filter_by(email=request.form['email']).first()
        if verify_user is not None:
            # If user was added, display success message
            flash('Your account was successfully created!')
            # Redirect to login page
            return redirect(url_for('/login'))
        else:
            # If user was not added, display message
            flash('There was an error creating your account. Please try again.')
            # Redirect to sign up page
            return redirect(url_for('/sign-up'))

#@app.route('/about')
#def about():
#    return render_template('about.html')

# You can add more routes as needed for different parts of your application

# For example, a routes that processes a form submission
#@app.route('/submit', methods=['POST'])
#def process_form():
 #   if request.method == 'POST':
        # Process form data here
        # You can access form data using request.form['fieldname']
        # After processing, you can redirect to another page
  #      return redirect(url_for('index'))

# You can add more routes to handle various aspects of your application

# Route to display a user's posts. Pass to template to display posts
#@app.route('/user/<int:user_id>')
#def user_profile(user_id):
#    user = User.query.get(user_id)
 #   user_posts = user.posts  # Get the user's posts
 #   return render_template('user_profile.html', user=user, user_posts=user_posts)