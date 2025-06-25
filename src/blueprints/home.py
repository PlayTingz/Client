import logging

import markdown
from flask import (
    Blueprint, flash, render_template, request
)
from markupsafe import Markup

from client import MCPClient

HomeBp = Blueprint('home', __name__, template_folder='templates')

@HomeBp.route('/', methods=(['GET', 'POST']))
async def index():
    data = None

    if request.method == 'POST':
        prompt = request.form['prompt']
        mcp = MCPClient()
        try:
            await mcp.initialize()
            response = await mcp.process_query(prompt)
            full_text = '\n'.join(str(message.content) for message in response['messages'])
            html_answer = Markup(markdown.markdown(full_text))
            data = {"prompt": prompt, "answer": html_answer}
        except Exception as e:
            logging.exception(e)
            flash("Could not process query. Please try again at a later time.")
        finally:
            await mcp.cleanup()

    return render_template('welcome.html', data=data)