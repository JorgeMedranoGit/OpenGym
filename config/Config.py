import os
from dotenv import load_dotenv


load_dotenv()

class Config: 
    SQLALCHEMY_DATABASE_URI = os.environ.get('OPENGYM_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False