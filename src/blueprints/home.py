import logging

import markdown
from flask import (
    Blueprint, flash, render_template, request
)
from markupsafe import Markup

from client import MCPClient
from config import UNITY_MCP_SERVER_DIR

HomeBp = Blueprint('home', __name__, template_folder='templates')

@HomeBp.route('/', methods=(['GET', 'POST']))
async def index():
    data = None

    if request.method == 'POST':
        prompt = request.form['prompt']
        mcp = MCPClient()
        try:
            await mcp.connect_to_server(UNITY_MCP_SERVER_DIR)
            full_text = await mcp.process_query(prompt)
            html_answer = Markup(markdown.markdown(full_text))
            data = {"prompt": prompt, "answer": html_answer}
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            flash("Could not process query. Please try again at a later time.")
        finally:
            await mcp.cleanup()

    return render_template('welcome.html', data=data)