from quart import Quart

from config import get_config


def create_app():
    app = Quart(__name__)

    app.config.from_object(get_config())

    from blueprints.home import HomeBp
    from blueprints.health import HealthBp

    app.register_blueprint(HomeBp)
    app.register_blueprint(HealthBp)
    app.add_url_rule('/', endpoint='index')

    return app


if __name__ == "__main__":
    app = create_app()

    host = app.config['HOST']
    port = app.config['PORT']
    debug = app.config['DEBUG']

    print(f"🚀 Starting server on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)