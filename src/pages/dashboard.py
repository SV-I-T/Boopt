import dash_mantine_components as dmc
from dash import register_page
from utils.login import checar_perfil

register_page(
    __name__, path="/app/dashboard", title="Minha Boopt", redirect_from=["/app"]
)


@checar_perfil
def layout():
    return [dmc.Title("Minha Boopt", order=1, weight=500)]
