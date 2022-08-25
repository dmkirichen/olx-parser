from flask_login import login_required, current_user
from flask import Blueprint, render_template
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/parse')
@login_required
def parse():
    return render_template('parse.html', access=current_user.access)
