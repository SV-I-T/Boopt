import dash_ag_grid as dag
import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, html, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask_login import current_user
from pydantic import ValidationError
from utils.banco_dados import db
from utils.modelo_assessment import AssessmentVendedor
from utils.modelo_usuario import Usuario, checar_login

register_page(
    __name__,
    path="/app/admin/assessment-vendedor/novo",
    title="Criar Assessment Vendedor",
)


@checar_login(admin=True, gestor=True)
def layout(empresa: str = None):
    texto_titulo = [
        "Novo Assessment Vendedor",
    ]
    layout_edicao = layout_novo_assessment(empresa)

    return [
        dmc.Title(texto_titulo, className="titulo-pagina"),
        layout_edicao,
    ]


def layout_novo_assessment(empresa: str = None):
    usr_atual: Usuario = current_user
    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in usr_atual.buscar_empresas()
    ]
    return html.Div(
        className="editar-assessment",
        children=[
            dmc.Group(
                mb="1rem",
                children=[
                    dmc.Select(
                        id="empresa-novo-av",
                        icon=DashIconify(icon="fluent:building-24-filled", width=24),
                        name="empresa",
                        data=data_empresas,
                        required=True,
                        searchable=True,
                        nothingFound="Não encontrei nada",
                        placeholder="Selecione uma empresa",
                        w=250,
                        value=empresa,
                    ),
                ],
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
                selectedRows={"ids": []},
                dashGridOptions={
                    "rowSelection": "multiple",
                    "suppressRowClickSelection": True,
                    "overlayLoadingTemplate": {
                        "function": "'<span>Selecione uma empresa primeiro</span>'"
                    },
                    "overlayNoRowsTemplate": {
                        "function": "'<span>Não há registros</span>'"
                    },
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
                className="ag-theme-quartz compact",
            ),
            dmc.Button(id="btn-criar-novo-av", children="Criar", mt="1rem"),
        ],
    )


@callback(
    Output("usuarios-av", "rowData"),
    Input("empresa-novo-av", "value"),
)
def carregar_usuarios_empresa(empresa: str):
    if not empresa:
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
    Output("notificacoes", "children"),
    Input("btn-criar-novo-av", "n_clicks"),
    State("empresa-novo-av", "value"),
    State("usuarios-av", "selectedRows"),
    prevent_initial_call=True,
)
def criar_assessment(n, empresa: str, linhas: list[dict[str, str]]):
    if not n:
        raise PreventUpdate
    elif not empresa:
        NOTIFICACAO = dmc.Notification(
            id="notificacao-sem-empresa",
            title="Atenção",
            message="Selecione uma empresa",
            action="show",
            color="orange",
        )
    elif not linhas:
        NOTIFICACAO = dmc.Notification(
            id="notificacao-sem-empresa",
            title="Atenção",
            message="Selecione pelo menos um usuário",
            action="show",
            color="orange",
        )
    else:
        participantes = [ObjectId(linha["_id"]) for linha in linhas]
        try:
            nova_aplicacao = AssessmentVendedor(
                empresa=ObjectId(empresa), participantes=participantes
            )
            nova_aplicacao.registrar()
        except ValidationError as e:
            erro = e.errors()[0]["ctx"]["error"]
            NOTIFICACAO = dmc.Notification(
                id="notificacao-erro-criacao-av",
                title="Erro",
                message=str(erro),
                action="show",
                color="red",
            )
        else:
            NOTIFICACAO = dmc.Notification(
                id="notificacao-sucesso-criacao-av",
                title="Pronto!",
                message="O Assessment Vendedor foi criado com sucesso",
                action="show",
                color="green",
            )

    return NOTIFICACAO
