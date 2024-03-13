import locale

from dash import Dash
from dash_app import layout
from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, url_for
from flask_login import current_user
from utils.banco_dados import mongo
from utils.cache import cache, cache_simple
from utils.email import mail
from utils.modelo_usuario import Usuario, login_manager

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
load_dotenv()

server = Flask(__name__, static_folder="assets")
server.config.from_prefixed_env()


@server.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@server.route("/login", methods=["GET"])
def login_get():
    if current_user and current_user.is_authenticated:
        return redirect("/app/dashboard")
    return render_template(
        "login.html",
        post_url=request.full_path,
    )


@server.route("/login", methods=["POST"])
def login_post():
    usr = request.form["user"]
    senha = request.form["password"]
    lembrar = bool(request.form.get("remember"))

    try:
        identificador = "email" if "@" in usr else "cpf"
        usr = Usuario.buscar(identificador=identificador, valor=usr)
        usr.validar_senha(senha)
    except AssertionError as e:
        return render_template("erro_login.html", mensagem=str(e))
    else:
        usr.logar(lembrar)
        next = request.args.get("next", None)
        next_url = "/app/dashboard" if next is None else next
        response = Response(
            "", status=302, headers={"HX-Redirect": next_url, "HX-Refresh": True}
        )
        return response


@server.route("/logout", methods=["POST", "GET"])
def logout_post():
    if current_user and current_user.is_authenticated:
        current_user.sair()
    return redirect("/")


@server.before_request
def checar_acesso():
    if not request.path.startswith("/app/") or (
        request.referrer and not request.referrer.startswith("/app/")
    ):
        return
    if current_user and current_user.is_authenticated:
        return
    return redirect(url_for("login_get", next=request.path))


app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
    use_pages=True,
    title="Boopt - Sucesso em Vendas",
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
