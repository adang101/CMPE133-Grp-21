from flask import render_template, Blueprint

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