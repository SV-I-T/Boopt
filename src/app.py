import locale

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
server.config.from_prefixed_env()

app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
    use_pages=True,
    update_title="Carregando...",
    external_scripts=[
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.10/dayjs.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.10/locale/pt-br.min.js",
    ],
)

mongo.init_app(server)
cache.init_app(server)
login_manager.init_app(server)

app.layout = layout()
app.enable_dev_tools(debug=False)


if __name__ == "__main__":
    server.run(load_dotenv=True)
