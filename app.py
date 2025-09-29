from flask import Flask
from config import Config
from db import db
from routes.job_route import job_bp
from flask_cors import CORS
from flask_migrate import Migrate
import os


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize migration engine
    Migrate(app, db)

    # Register blueprints
    app.register_blueprint(job_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=False
    )
