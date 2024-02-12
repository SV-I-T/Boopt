import dash_mantine_components as dmc
from dash import register_page

register_page(__name__, path="/admin/empresas", title="Gerenciar Empresas")


def layout():
    return [dmc.Title("Gerenciamento de empresas", order=1, weight=700)]
