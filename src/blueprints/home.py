import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

HomeBp = Blueprint('home', __name__, template_folder='templates')

@HomeBp.route('/', methods=(['GET']))
def index():
    if request.method == 'POST':
        person = request.form['person']
        error = None
        if not person:
            error = 'person is required.'
    print('Home')
    return render_template('welcome.html')