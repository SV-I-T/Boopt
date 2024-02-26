import dash_mantine_components as dmc
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
    return [dmc.Title("Bem-vindo ao Assessment de Vendedor")]
