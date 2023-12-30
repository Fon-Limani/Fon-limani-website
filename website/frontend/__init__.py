import os

from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail
from flask_oauthlib.client import OAuth



load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)
mail.init_app(app)

oauth = OAuth(app)
google = oauth.remote_app(
    "google",
    consumer_key=os.getenv("GOOGLE_CLIENT_ID"),
    consumer_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    request_token_params={
        "scope": "email",
    },
    base_url="https://www.googleapis.com/oauth2/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
)

from frontend import routes