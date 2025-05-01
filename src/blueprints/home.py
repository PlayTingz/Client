import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import markdown
from markupsafe import Markup
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
            # If message.content is a list of TextBlock-like objects
            full_text = "\n\n".join(block.text for block in answer if hasattr(block, "text"))
            html_answer = Markup(markdown.markdown(full_text))  # convert markdown to HTML
            data = {"prompt": prompt, "answer": html_answer}
            return render_template('welcome.html', data=data)
    return render_template('welcome.html')