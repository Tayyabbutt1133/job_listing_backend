from flask import Flask
from config import Config
from db import db
from routes.job_route import job_bp
from flask_cors import CORS
from Scraper.scrape import scrape_actuary_jobs

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

