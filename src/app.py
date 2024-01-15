import locale
import os
import secrets

from dash import Dash
from dash_app import layout
from dotenv import load_dotenv
from flask import Flask
from utils.banco_dados import mongo
from utils.cache import cache
from utils.login import login_manager

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
load_dotenv()

server = Flask(__name__)
server.config["SECRET_KEY"] = secrets.token_hex()
server.config["MONGO_URI"] = os.environ.get("MONGO_URI")

app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
    use_pages=True,
    update_title=None,
)

mongo.init_app(server)
cache.init_app(server)
login_manager.init_app(server)

app.layout = layout()


if __name__ == "__main__":
    server.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
