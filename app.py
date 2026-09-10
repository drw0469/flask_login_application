from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from functools import wraps

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os

app = Flask(__name__)
# Replace this with a secure secrect key in production
# app.config['SECRET_KEY'] = 'super_secret_key'
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.update(
    SESSION_COOKIE_SECURE=True,    # Only sends cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevents JavaScript from reading the cookie
    SESSION_COOKIE_SAMESITE='Lax', # Mitigates Cross-Site Request Forgery (CSRF)
)


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirects unauthenticated users here

# Custom Decorator for Admin-Only Routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check if user is logged in
        # 2. Check if their role is 'admin'
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)  # HTTP 403 Forbidden Error
        return f(*args, **kwargs)
    return decorated_function


# Define User Model
# UserMixin provides the default attributes required by Flask-Login (e.g. is_authenticated)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def home():
    return render_template("base.html")

@app.route("/register", methods=['GET', "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username already exists
        existing_user = db.session.scalars(select(User).filter_by(username=username)).first()
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))

        # Hash the password before saving to the database
        hashed_password = generate_password_hash(password, method='scrypt')

        # NOTE: For security, we hardcode the role as 'user' here so malicious users 
        # cannot pass a raw form field injection to grant themselves admin privileges.
        new_user = User(username=username, password=hashed_password, role="user")

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# Define your form class
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

limiter = Limiter(get_remote_address, app=app)

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = db.session.scalars(select(User).filter_by(username=username)).first()

        # Verify the user exists and the password matches
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)

@app.route('/dashboard')
@login_required # This restricts access to authenticated users only
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route("/admin")
@admin_required  # Custom decorator applied here
def admin_panel():
    # Fetch all users to display them on the admin board
    all_users = db.session.scalars(select(User)).all()
    return render_template('admin.html', users=all_users)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# Initialize database tables
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
