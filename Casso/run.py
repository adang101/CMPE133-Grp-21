from flask import render_template
from flask_login import LoginManager
from app import create_app
import os

app = create_app()

app.secret_key = os.environ.get('SECRET_KEY', 'ALVIN_DID_THE_ENTIRE_WEB_DEVELOPMENT')

# Login User Session Management
login_manager = LoginManager()
login_manager.init_app(app)

# User Loader
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.get(user_id)

from app.models import User

# Path to landing page (index.html)
@app.route('/')
def index():
    return render_template('/')

if __name__ == '__main__':
    app.run(debug=False) # Set debug to False when deploying to production