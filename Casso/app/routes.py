from flask import render_template, Blueprint, request, redirect, url_for, flash, get_flashed_messages, current_app as app
from flask_login import login_required, login_user, logout_user, current_user
from .models import User, db, Post
from werkzeug.security import check_password_hash, generate_password_hash
import re, os
from werkzeug.utils import secure_filename

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

# Handle login form submission
@bp.route('/login-request', methods=['POST'])
def login_form():
    if request.method == 'POST':
        # Get username and password from form
        email = request.form['email']
        password = request.form['password']

        # Query the database to get the user with the username
        user = User.query.filter_by(email=email).first()

        # Check if the user exists in the database
        if user is not None:
            # If user exists, check if the password matches
            if user.password == password:
                # If password matches, log in user and being user session
                flash('You were successfully logged in!')
                login_user(user)

                return render_template('index.html', messages=get_flashed_messages())
            else:
                # If password does not match, display message
                flash('Incorrect password. Please try again.')
                return render_template('login.html', messages=get_flashed_messages())
        else:
            # If email does not exist, display message
            flash('Email does not exist. Please try again.')
            return render_template('login.html', messages=get_flashed_messages())

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

        new_full_name = request.form['full-name']
        new_user = request.form['username']
        new_email = request.form['email']
        new_password = request.form['password']
        check_password = request.form['check-password']

        # Check if the username or email already exists in the database
        verify_username = User.query.filter_by(username=new_user).first()
        if verify_username is not None:
            flash('Username already exists. Please try again.')
            return render_template('sign-up.html', messages=get_flashed_messages())

        verify_email = User.query.filter_by(email=new_email).first()
        if verify_email is not None:
            flash('Email already exists. Please try again.')
            return render_template('sign-up.html', messages=get_flashed_messages())

        verify_full_name = User.query.filter_by(full_name=new_full_name).first()
        if verify_full_name is not None:
            flash('Full name already exists. Please try again.')
            return render_template('sign-up.html', messages=get_flashed_messages())

        # Check if email is in a valid format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", request.form['email']):
            flash('Email is not in a valid format. Please enter a valid email address.')
            return render_template('sign-up.html', messages=get_flashed_messages())
        
        # Check if password and check password fields match
        if new_password != check_password:
            flash('Passwords do not match. Please try again.')
            return render_template('sign-up.html', messages=get_flashed_messages())
        
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
            return render_template('login.html', messages=get_flashed_messages())
        else:
            # If user was not added, display message
            flash('There was an error creating your account. Please try again.')
            # Redirect to sign up page
            return render_template('sign-up.html', messages=get_flashed_messages())

# Path to Profile view (profile.html) - Requires user to be logged in
@bp.route('/profile-settings')
@login_required
def profile():
    return render_template('profile-settings.html')

# Handle biography form submission
@bp.route('/update-biography', methods=['POST'])
@login_required
def update_biography():
    new_biography = request.form['biography']
    current_user.biography = new_biography
    db.session.commit()
    flash('Your biography has been updated.')
    return render_template('profile-settings.html')

# Handle password form submission
@bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    new_password = request.form['new_password']
    check_password = request.form['current_password']
    # Check if password and check password fields match
    if check_password_hash(current_user.password, check_password):
        flash('Your current password was entered incorrectly. Please try again.')
        return render_template('profile-settings.html', messages=get_flashed_messages())
    else:
        # Check if confirm password is same as new password
        confirm_password = request.form['confirm_password']
        if confirm_password != new_password:
            flash('Passwords do not match. Please try again.')
            return render_template('profile-settings.html', messages=get_flashed_messages())
        else:
            current_user.password = new_password
            db.session.commit()
            flash('Your password has been updated.')
            return render_template('profile-settings.html', messages=get_flashed_messages())
    
# Handle profile picture form submission
@bp.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']

        if file.filename != '':
            # Check if the file extension is allowed
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
                # Generate a unique filename for the uploaded picture, e.g., based on the user's ID
                filename = f"user_{current_user.id}_{secure_filename(file.filename)}"

                # Ensure the upload folder exists
                os.makedirs(app.config['UPLOAD_FOLDER_PROFILE_PICS'], exist_ok=True)

                # Save the file to a userPhotos folder in your static directory
                file.save(os.path.join(app.config['UPLOAD_FOLDER_PROFILE_PICS'], filename))

                # Update the user's profile_picture field with the filename
                current_user.profile_picture = filename
                db.session.commit()
            else:
                flash('File type not allowed. Please upload a PNG, JPG, or JPEG file.')

    return render_template('profile-settings.html')

# Handle user sign out request - Requires user to be logged in
@bp.route("/sign-out")
@login_required
def logout():
    logout_user()
    return render_template('index.html')

# Path to Home Feed (home-feed.html) - Requires user to be logged in
@bp.route('/home-feed')
@login_required
def home_feed():
    page_name = 'Home Feed'
    #return render_template('home-feed.html', page_name=page_name)
    # This fetches all posts; you can modify the query as needed
    posts = Post.query.all()
    return render_template('home-feed.html', posts=posts, page_name=page_name)

# Path to create a post page (create-page.html) - Requires user to be logged in
@bp.route('/create-page')
@login_required
def create_page():
    return render_template('create-page.html')

# Handle create post form submission
@bp.route('/create-post', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        image = request.files['image']
                # Save the file to a userPhotos folder in your static directory
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Update the user's profile_picture field with the filename
                #current_user.profile_picture = filename
                #db.session.commit()
        # Check if the file extension is allowed
        if image and '.' in image.filename and image.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
            # Generate image file name
            filename = secure_filename(image.filename)

            # Ensure the upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER_POSTS'], exist_ok=True)

            image_path = os.path.join(app.config['UPLOAD_FOLDER_POSTS'], filename)
            image.save(image_path)

            new_post = Post(title=title, image=filename, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully.')
            return render_template('create-page.html', messages=get_flashed_messages())
        else:
            flash('File type not allowed. Please upload a PNG, JPG, or JPEG file.')
    return render_template('home-feed.html')

 # Handle navigation to a user's profile page

@bp.route('/view-profile')
@login_required
def current_user_profile():
    # You can directly access the current user using current_user
    user = current_user
    user_posts = user.posts  # Get the user's posts
    name = user.full_name
    username = user.username
    bio = user.biography
    profile_pic = user.profile_picture

    return render_template('view-profile.html', user=user, user_posts=user_posts, name=name, username=username, bio=bio, profile_pic=profile_pic)

# Load X user profile views
@bp.route('/user/<int:user_id>')
def user(user_id):
    user = User.query.get(user_id)
    user_posts = user.posts  # Get the user's posts
    name = user.full_name
    username = user.username
    bio = user.biography
    profile_pic = user.profile_picture

    return render_template('view-profile.html', user=user, user_posts=user_posts, name=name, username=username, bio=bio, profile_pic=profile_pic)

# Load current user chat page
@bp.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

# Route to display a user's posts. Pass to template to display posts
#@app.route('/user/<int:user_id>')
#def user_profile(user_id):
#    user = User.query.get(user_id)
 #   user_posts = user.posts  # Get the user's posts
 #   return render_template('user_profile.html', user=user, user_posts=user_posts)