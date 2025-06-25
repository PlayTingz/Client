import socket

from quart import (
    Blueprint, jsonify
)

HealthBp = Blueprint('health', __name__, url_prefix='/health')

@HealthBp.route('/', methods=(['GET']))
async def health():
    host_name, host_ip = await fetchDetails()
    return jsonify(
        host=host_name,
        ip=host_ip,
        status="Up"
    )

@HealthBp.route('/test-host', methods=(['GET']))
async def fetchDetails():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return str(host_name), str(host_ip)