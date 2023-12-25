from flask import render_template
from flask_login import LoginManager
from app import create_app

app = create_app()

app.secret_key = 'ALVIN_DID_THE_ENTIRE_WEB_DEVELOPMENT'

# Login User Session Management
login_manager = LoginManager()
login_manager.init_app(app)

# User Loader
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.get(user_id)

from app.models import User

if __name__ == '__main__':
    app.run(debug=False)