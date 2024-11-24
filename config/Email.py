class Email:
    MAIL_SERVER = 'in-v3.mailjet.com'
    MAIL_PORT = 587  
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'd9fcf5ddb82dd006f25ba4a1cbc15384'
    MAIL_PASSWORD = '91b7892eebb80f2470bdf4d99a6a058c'  
    MAIL_DEFAULT_SENDER = 'quantumcodersunivalle@gmail.com' 




""" import os
from dotenv import load_dotenv

load_dotenv()

class Email:
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') """