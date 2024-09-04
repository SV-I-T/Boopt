import locale

from dash import Dash
from dotenv import load_dotenv
from flask import Flask, Response

from dash_app import layout
from utils.banco_dados import mongo

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
load_dotenv()

server = Flask(__name__, static_folder="assets")
server.config.from_prefixed_env()


@server.get("/logout")
def logout():
    return Response(status=401)


app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
    use_pages=True,
    title="Boopt - Sucesso em Vendas",
    update_title="Carregando...",
    external_scripts=["https://cdn.plot.ly/plotly-locale-pt-br-latest.js"],
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap"
    ],
    meta_tags=[{"name": "theme-color", "content": "#f3f3f3"}],
)

mongo.init_app(server)

app.layout = layout
app.enable_dev_tools(debug=None)

if __name__ == "__main__":
    # server.run(load_dotenv=True, port=8080, host="127.0.0.1")
    server.run(load_dotenv=True, port=8080, host="0.0.0.0")
