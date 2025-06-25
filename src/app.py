import os

from quart import Quart

from config import config


def create_app(config_mode):
    app = Quart(__name__)
    app.config.from_object(config[config_mode])

    # Set up routes
    from blueprints.home import HomeBp
    from blueprints.health import HealthBp

    app.register_blueprint(HomeBp)
    app.register_blueprint(HealthBp)
    app.add_url_rule('/', endpoint='index')
    return app

app = create_app(os.getenv("CONFIG_MODE", "development"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
