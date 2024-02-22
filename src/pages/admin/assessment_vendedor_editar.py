import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_ag_grid import AgGrid
from dash_iconify import DashIconify
from utils.banco_dados import db
from utils.modelo_usuario import checar_login

register_page(
    __name__, path="/admin/assessment-vendedor/edit", title="Editar Assessment Vendedor"
)


@checar_login
def layout(id: str = None):
    texto_titulo = [
        "Novo Assessment Vendedor",
    ]
    layout_edicao = layout_novo_assessment()

    return [
        dmc.Title(texto_titulo, order=1, weight=700),
        layout_edicao,
    ]


def layout_novo_assessment():
    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in db("Boopt", "Empresas").find(
            projection={"_id": 1, "nome": 1}, sort={"nome": 1}
        )
    ]
    return html.Div(
        style={"maxWidth": 300},
        children=[
            dmc.Select(
                id="empresa-novo-av",
                label="Empresa",
                icon=DashIconify(icon="fluent:building-24-filled", width=24),
                name="empresa",
                data=data_empresas,
                required=True,
                searchable=True,
                nothingFound="Não encontrei nada",
                value=None,
            ),
            dmc.ActionIcon(
                id="usuarios-atualizar-btn-av",
                children=DashIconify(
                    icon="fluent:arrow-clockwise-20-regular", width=20
                ),
                color="theme.primaryColor",
                variant="filled",
            ),
            AgGrid(
                id="usuarios-av",
                rowData=[
                    {"_id": "1", "usuario": "Fulano", "cargo": "Vendedor"},
                    {"_id": "2", "usuario": "Ciclano", "cargo": "Vendedor II"},
                ],
                columnDefs=[
                    {"field": "_id", "hide": True},
                    {"field": "usuario"},
                    {"field": "cargo"},
                ],
                defaultColDef={"filter": True, "floatingFilter": True},
            ),
            dmc.Button(id="btn-criar-novo-av", children="Criar"),
            html.Div(id="feedback-novo-av"),
        ],
    )


# @callback(
#     Output()
# )
