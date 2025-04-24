import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

HomeBp = Blueprint('home', __name__, template_folder='templates')

@HomeBp.route('/', methods=(['GET', 'POST']))
def index():
    if request.method == 'POST':
        print('Home')
        prompt = request.form['prompt']
        error = None
        if not prompt:
            error = 'prompt is required.'
        if error is not None:
            flash(error)
        else:
            # pass prompt to service to initiate MCP-Protocol action in unity
            answer = "MCP-Generated Answer"
            data = {
                'answer': answer,
                'prompt': prompt
            }
            return render_template('welcome.html', data=data)
    return render_template('welcome.html')