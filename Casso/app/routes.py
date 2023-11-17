from flask import render_template, Blueprint, request, redirect, url_for, flash, get_flashed_messages, current_app as app
from flask_login import login_required, login_user, logout_user, current_user
from .models import User, db, Post, Message, ChatSession, CommissionRequest
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func
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
def default_chat():
    # return render_template('chat.html')
    # Retrieve chat sessions for the current user
    user_chat_sessions = ChatSession.query.filter(
        (ChatSession.user1_id == current_user.id) | (ChatSession.user2_id == current_user.id)
        ).outerjoin(Message).group_by(ChatSession).order_by(func.coalesce(func.max(Message.created_at), ChatSession.created_at).desc()).all()
    most_recent_chat_session = user_chat_sessions[0] if user_chat_sessions else None
    messages = most_recent_chat_session.messages.order_by(Message.created_at.asc()).all() if most_recent_chat_session else []
    return render_template('chat.html', user_chat_sessions=user_chat_sessions, current_chat_session=most_recent_chat_session, messages=messages)

# Load chat session for chat.html
@bp.route('/chat/<int:chat_session_id>', methods=['GET', 'POST'])
@login_required
def chat_session(chat_session_id):
    curr_chat_session = ChatSession.query.get_or_404(chat_session_id)
    user_chat_sessions = (ChatSession.query.filter(
            (ChatSession.user1_id == current_user.id) | (ChatSession.user2_id == current_user.id))
            .order_by(db.func.coalesce(Message.created_at, ChatSession.created_at).desc()).all())
    # Pagination. Work on it later messages = chat_session.messages.order_by(Message.created_at.asc()).limit(14).all()
    messages = curr_chat_session.messages.order_by(Message.created_at.asc()).all()

    if request.method == 'POST':
        # Handle sending a new message (add logic to store the message)
        new_message_content = request.form.get('message_input')
        if new_message_content:
            new_message = Message(sender_id=current_user.id, receiver_id=curr_chat_session.user2_id, content=new_message_content, chat_session_id=curr_chat_session.id)
            db.session.add(new_message)
            db.session.commit()
        return redirect(url_for('chat_session', chat_session_id=curr_chat_session.id))

    return render_template('chat.html', user_chat_sessions=user_chat_sessions, current_chat_session=curr_chat_session, messages=messages)


# Load more messages for chat.html current chat session
'''@bp.route('/load_more_messages/<int:chat_session_id>/<int:last_message_id>')
@login_required
def load_more_messages(chat_session_id, last_message_id):
    chat_session = ChatSession.query.get_or_404(chat_session_id)
    more_messages = load_more_messages(chat_session, last_message_id)

    # Render and return the HTML for the new messages
    return render_template('_message_list.html', messages=more_messages)'''

# Route to display a user's posts. Pass to template to display posts
#@app.route('/user/<int:user_id>')
#def user_profile(user_id):
#    user = User.query.get(user_id)
 #   user_posts = user.posts  # Get the user's posts
 #   return render_template('user_profile.html', user=user, user_posts=user_posts)