# app.py
import os
from flask import request, jsonify
import socket
from create_app import create_app

app = create_app(os.getenv("CONFIG_MODE","development"))

@app.route('/test-host')
def fetchDetails():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return str(host_name), str(host_ip)

@app.route("/health")
def health():
    host_name, host_ip = fetchDetails()
    return jsonify(
        host=host_name,
        ip=host_ip,
        status="Up"
    )
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv("PORT", 5000), debug=True)