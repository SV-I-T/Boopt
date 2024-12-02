import locale
import os
import re
from datetime import datetime, timedelta

from dash import CeleryManager, Dash, DiskcacheManager
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_mail import Message
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from werkzeug.security import generate_password_hash

from components.dash_app import layout
from utils.banco_dados import mongo
from utils.cache import cache, cache_simple
from utils.email import attach_logo, mail
from utils.login import login_manager
from utils.usuario import Usuario

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
load_dotenv()

server = Flask(__name__)
server.config.from_prefixed_env()


@server.route("/", methods=["GET"])
def landing_page():
    return render_template("lp.html")


@server.route("/login", methods=["GET"])
def login_get():
    if current_user and current_user.is_authenticated:
        return redirect("/app/vela")
    return render_template(
        "login.html",
        post_url=request.full_path,
    )


@server.route("/login", methods=["POST"])
def login_post():
    login = request.form["login"]
    senha = request.form["password"]
    lembrar = bool(request.form.get("remember"))

    try:
        identificador = "email" if "@" in login else "cpf"
        usr = Usuario.consultar(identificador=identificador, valor=login)
        usr.validar_senha(senha)
    except AssertionError as e:
        return render_template("login.html", mensagem=str(e), status="status-error")
    else:
        login_user(usr, remember=lembrar, force=True)
        next_url = request.args.get("next", None) or "/app/dashboard"
        response = redirect(next_url)
        return response


@server.route("/logout", methods=["POST", "GET"])
def logout_post():
    usr_atual = Usuario.atual()
    if usr_atual and usr_atual.is_authenticated:
        cache_simple.delete_memoized(Usuario.consultar_pelo_id, Usuario, usr_atual.id)
        logout_user()
    return redirect("/")


# @server.route("/forgot-password", methods=["GET"])
# def forgot_password_get():
#     return render_template("recover_password.html")


# @server.route("/forgot-password/<string:token>", methods=["GET"])
# def forgot_password_get_token(token: str):
#     try:
#         payload = jwt.decode(
#             token, key=os.environ["FLASK_SECRET_KEY"], algorithms="HS256"
#         )
#     except ExpiredSignatureError:
#         return render_template(
#             "recover_password.html", success=False, message="Este link expirou."
#         )
#     try:
#         usr_id: str = payload["id"]
#         usr = Usuario.consultar("_id", usr_id)
#         nova_senha = usr.data.strftime("%d%m%Y")
#         usr.atualizar({"senha_hash": generate_password_hash(nova_senha)})
#     except Exception:
#         render_template(
#             "recover_password.html",
#             success=False,
#             message="Desculpe, algo de errado aconteceu. Por favor, tente novamente.",
#         )

#     return render_template("recover_password.html", success=True)


# @server.route("/forgot-password", methods=["POST"])
# def forgot_password_post():
#     login = request.form["login"]
#     identificador = "email" if "@" in login else "cpf"

#     try:
#         usr = Usuario.consultar(identificador=identificador, valor=login)
#     except AssertionError:
#         if identificador == "email":
#             return render_template(
#                 "recover_password.html",
#                 mensagem="Não encontramos um cadastro com este e-mail. Por favor, tente novamente com o seu CPF.",
#                 status="status-error",
#             )
#         else:
#             return render_template(
#                 "recover_password.html",
#                 mensagem="Não encontramos um cadastro com este CPF. Por favor, entre em contato com o seu gestor/responsável.",
#                 status="status-error",
#             )
#     if not usr.email:
#         return render_template(
#             "recover_password.html",
#             mensagem="Este cadastro não possui um e-mail vinculado para recuperar a senha. Por favor, solicite para o seu gestor/responsável a redefinição da sua senha ao padrão. Recomendamos que adicione um e-mail após recuperar seu acesso.",
#             status="status-error",
#         )

#     now = datetime.now()
#     exp = now + timedelta(hours=1)
#     payload = {"id": usr.id, "iat": now.timestamp(), "exp": exp.timestamp()}
#     token = jwt.encode(payload, key=os.environ["FLASK_SECRET_KEY"])

#     msg = Message(
#         subject="Boopt - Recuperação de senha",
#         html=render_template(
#             "email/recover_password.html",
#             nome=usr.nome,
#             link=f"{request.host_url}forgot-password/{token}",
#         ),
#         recipients=[usr.email],
#     )
#     attach_logo(msg)
#     mail.send(msg)
#     email_obfuscado = re.sub(
#         r"(?<=.)[^@](?=[^@]*?[^@]@)|(?:(?<=@.)|(?!^)\\G(?=[^@]*$)).(?=.*[^@]\\.)",
#         "*",
#         usr.email,
#     )
#     return render_template(
#         "recover_password.html",
#         mensagem=f"Enviamos um link para redefinição da senha no e-mail {email_obfuscado}.",
#         status="status-info",
#     )


@server.before_request
def checar_acesso():
    if not request.path.startswith("/app/") or (
        request.referrer and not request.referrer.startswith("/app/")
    ):
        return
    if current_user and current_user.is_authenticated:
        return
    return redirect(url_for("login_get", next=request.path))


if "CELERY" in os.environ:
    from celery import Celery

    celery_app = Celery(
        __name__, broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
    )
    background_callback_manager = CeleryManager(celery_app)
else:
    import diskcache

    background_callback_manager = DiskcacheManager(diskcache.Cache("./cache"))

dash = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
    use_pages=True,
    title="Boopt - Sucesso em Vendas",
    update_title="Carregando...",
    external_scripts=[
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.10/dayjs.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.11.10/locale/pt-br.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/helpers.min.js",
        "https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0",
    ],
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap",
    ],
    meta_tags=[{"name": "theme-color", "content": "#f2f2f2"}],
    assets_folder="static",
    serve_locally=os.environ["DASH_DEBUG"] == "true",
    background_callback_manager=background_callback_manager,
)

mongo.init_app(server)
cache.init_app(server)
cache_simple.init_app(server)
login_manager.init_app(server)
# mail.init_app(server)

dash.layout = layout
dash.enable_dev_tools(debug=None)

if __name__ == "__main__":
    # server.run(load_dotenv=True, port=8080, host="127.0.0.1")
    server.run(load_dotenv=True, port=8080, host="0.0.0.0")
