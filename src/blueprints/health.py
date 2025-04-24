import functools
import socket

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

HealthBp = Blueprint('health', __name__, url_prefix='/health')

@HealthBp.route('/', methods=(['GET']))
def health():
    host_name, host_ip = fetchDetails()
    return jsonify(
        host=host_name,
        ip=host_ip,
        status="Up"
    )

@HealthBp.route('/test-host', methods=(['GET']))
def fetchDetails():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return str(host_name), str(host_ip)
