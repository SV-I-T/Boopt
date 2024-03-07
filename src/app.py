import locale

from dash import Dash
from dash_app import layout
from dotenv import load_dotenv
from flask import Flask
from utils.banco_dados import mongo
from utils.cache import cache, cache_simple
from utils.email import mail
from utils.modelo_usuario import login_manager

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
load_dotenv()

server = Flask(__name__)
server.config.from_prefixed_env()

app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
    use_pages=True,
    update_title="Carregando...",
    external_scripts=[
        "https://cdn.plot.ly/plotly-locale-pt-br-latest.js",
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.10/dayjs.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.10/locale/pt-br.min.js",
    ],
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap"
    ],
)

mongo.init_app(server)
cache.init_app(server)
cache_simple.init_app(server)
login_manager.init_app(server)
mail.init_app(server)

app.layout = layout
app.enable_dev_tools(debug=None)


if __name__ == "__main__":
    server.run(load_dotenv=True, port=8080, host="127.0.0.1")
