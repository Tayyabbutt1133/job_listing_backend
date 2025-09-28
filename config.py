import os
from dotenv import load_dotenv



load_dotenv()



class Config:
    # PostgreSQL connection
    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRES_DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
