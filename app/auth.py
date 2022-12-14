from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    access_level = request.form.get('access')

    user = User.query.filter_by(email=email).first()
    if user:  # user with such email already exists
        flash('User with such email already exists')
        return redirect(url_for('auth.signup'))

    # Adding new user to the database
    new_user = User(email=email, password=generate_password_hash(password, method='sha256'), access=access_level)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['POST'])
def login_post():
    print(request.form)
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user:  # such user does not exist
        flash("User with such email does not exist.")
        return redirect(url_for('auth.login'))

    if not check_password_hash(user.password, password):
        flash("Wrong password, try again.")
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.parse'))
