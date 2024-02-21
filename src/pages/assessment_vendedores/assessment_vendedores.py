from dash import register_page
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Usuario, checar_login

register_page(
    __name__,
    path="/assessment-vendedor",
    title="Assessment Vendedor",
    redirect_from=["/dashboard"],
)


@checar_login
def layout():
    usr: Usuario = current_user
    return None
