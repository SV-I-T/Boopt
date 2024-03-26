import dash_mantine_components as dmc
from dash import register_page
from flask_login import current_user
from utils.modelo_usuario import Usuario, checar_login

register_page(
    __name__, path="/app/dashboard", title="Dashboard", redirect_from=["/app"]
)


@checar_login
def layout():
    return [dmc.Title("Minha Boopt", order=1, weight=500)]
