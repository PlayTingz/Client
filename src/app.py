# app.py
import os
from flask import request, jsonify
from create_app import create_app

app = create_app(os.getenv("CONFIG_MODE","development"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv("PORT", 5000), debug=True)