from flask import Flask
from config import Config
from db import db
from routes.job_route import job_bp
from flask_cors import CORS
from Scraper.scrape import scrape_actuary_jobs
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(job_bp)
    return app


app = create_app()

with app.app_context():
    scrape_actuary_jobs()
    db.create_all()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=False
    )
