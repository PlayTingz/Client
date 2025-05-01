import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from ai.anthropicClient import AnthropicClient

HomeBp = Blueprint('home', __name__, template_folder='templates')

@HomeBp.route('/', methods=(['GET', 'POST']))
def index():
    if request.method == 'POST':
        prompt = request.form['prompt']
        error = None
        if not prompt:
            error = 'prompt is required.'
        if error is not None:
            flash(error)
        else:
            #use anthropic 
            anthropic = AnthropicClient()
            # pass prompt to service to initiate MCP-Protocol action in unity
            answer = anthropic.prompt(prompt)
            print(answer)
            data = {
                'answer': answer,
                'prompt': prompt
            }
            return render_template('welcome.html', data=data)
    return render_template('welcome.html')