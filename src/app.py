import locale
import secrets

from flask import Flask
from dotenv import load_dotenv

from .utils.banco_dados import mongo
from .utils.cache import cache
from dash_app import app
from .utils.login import login_manager

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

load_dotenv()

server = Flask(__name__)
server.config["SECRET_KEY"] = secrets.token_hex()

mongo.init_app(server)
cache.init_app(server)
app.init_app(server)
login_manager.init_app(server)

if __name__ == "__main__":
    server.run(debug=True)
