import dash_ag_grid as dag
import dash_mantine_components as dmc
from bson import ObjectId
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
            dag.AgGrid(
                id="usuarios-av",
                columnDefs=[
                    {
                        "field": "_id",
                        "hide": True,
                    },
                    {
                        "headerName": "Usuário",
                        "field": "usuario",
                        "checkboxSelection": True,
                        "headerCheckboxSelection": True,
                        "headerCheckboxSelectionFilteredOnly": True,
                    },
                    {"field": "cargo"},
                ],
                getRowId="params.data._id",
                selectedRows={"ids": ["10"]},
                rowData=[
                    {
                        "_id": "10",
                        "usuario": "Fulano",
                        "cargo": "Vendedor",
                    },
                    {
                        "_id": "2",
                        "usuario": "Ciclano",
                        "cargo": "Vendedor II",
                    },
                ],
                dashGridOptions={
                    "rowSelection": "multiple",
                    "suppressRowClickSelection": True,
                },
                defaultColDef={
                    "resizable": False,
                    "filter": True,
                    "floatingFilter": True,
                    "floatingFilterComponentParams": {
                        "suppressFilterButton": True,
                    },
                    "suppressMenu": True,
                    "suppressMovable": True,
                    "flex": 1,
                },
                style={"width": 500},
                className="ag-theme-quartz compact",
            ),
            dmc.Button(id="btn-criar-novo-av", children="Criar"),
            html.Div(id="feedback-novo-av"),
        ],
    )


@callback(
    Output("usuarios-av", "rowData"),
    Input("usuarios-atualizar-btn-av", "n_clicks"),
    State("empresa-novo-av", "value"),
    prevent_initial_call=True,
)
def carregar_usuarios_empresa(n: int, empresa: str):
    if not n:
        raise PreventUpdate

    usuarios = list(
        db("Boopt", "Usuários").find(
            {"empresa": ObjectId(empresa)},
            {
                "_id": {"$toString": "$_id"},
                "usuario": {"$concat": ["$nome", " ", "$sobrenome"]},
                "cargo": 1,
            },
        )
    )

    return usuarios


@callback(
    Output("usuarios-av", "children"),
    Input("btn-criar-novo-av", "n_clicks"),
    State("usuarios-av", "selectedRows"),
    prevent_initial_call=True,
)
def ler_linhas_selecionadas(n, linhas: list[dict[str, str]]):
    print(linhas)
    raise PreventUpdate
