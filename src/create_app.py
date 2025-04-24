from flask import Flask
from config import config

# db = SQLAlchemy()
# db = MongoEngine()
# migrate = Migrate()

def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config[config_mode])
    
    # Set up routes
    from blueprints.home import HomeBp
    from blueprints.health import HealthBp
    
    app.register_blueprint(HomeBp)
    app.register_blueprint(HealthBp)
    app.add_url_rule('/', endpoint='index')
    return app