from datetime import datetime

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
from utils.modelo_usuario import Perfil, Usuario, checar_perfil

register_page(
    __name__,
    path="/app/admin/assessment-vendedor/edit",
    title="Criar Assessment Vendedor",
)


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout(empresa: str = None, id: str = None):
    texto_titulo = [
        "Novo Assessment Vendedor",
    ]
    layout_edicao = layout_novo_assessment(empresa, id)

    return [
        dmc.Title(texto_titulo, className="titulo-pagina"),
        layout_edicao,
    ]


def layout_novo_assessment(empresa: str = None, id: str = None):
    usr: Usuario = current_user
    data_empresas = (
        [
            {"value": str(_empresa["_id"]), "label": _empresa["nome"]}
            for _empresa in usr.buscar_empresas()
        ]
        if usr.perfil != Perfil.gestor
        else [str(usr.empresa)]
    )

    if id:
        assessment = AssessmentVendedor(
            **db("AssessmentVendedores", "Aplicações").find_one({"_id": ObjectId(id)})
        )
    else:
        assessment = None

    return html.Div(
        className="editar-assessment",
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
                value=str(assessment.empresa)
                if id
                else empresa
                if empresa
                else str(usr.empresa),
                w=250,
                mb="1rem",
                disabled=bool(id),
            ),
            dmc.TextInput(
                label="Descrição",
                id="descricao-novo-av",
                required=True,
                value=assessment.descricao
                if id
                else f'Aplicação - {datetime.now().strftime("%d/%m/%Y")}',
                mb="1rem",
            ),
            dag.AgGrid(
                id="usuarios-av",
                columnDefs=[
                    {
                        "field": "id",
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
                getRowId="params.data.id",
                rowData=list(
                    db("Boopt", "Usuários").find(
                        {
                            "empresa": ObjectId(
                                assessment.empresa
                                if id
                                else empresa
                                if empresa
                                else usr.empresa
                            )
                        },
                        {
                            "_id": 0,
                            "id": {"$toString": "$_id"},
                            "usuario": {"$concat": ["$nome", " ", "$sobrenome"]},
                            "cargo": 1,
                        },
                    )
                ),
                selectedRows=[{"id": str(id)} for id in assessment.participantes]
                if id
                else [],
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
            dmc.Button(
                id="btn-salvar-av" if id else "btn-criar-av",
                children="Salvar" if id else "Criar",
                mt="1rem",
            ),
        ],
    )


@callback(
    Output("usuarios-av", "rowData"),
    Input("empresa-novo-av", "value"),
    prevent_initial_call=True,
)
def carregar_usuarios_empresa(empresa: str):
    if not empresa:
        raise PreventUpdate

    usuarios = list(
        db("Boopt", "Usuários").find(
            {"empresa": ObjectId(empresa)},
            {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "usuario": {"$concat": ["$nome", " ", "$sobrenome"]},
                "cargo": 1,
            },
        )
    )

    return usuarios


# @callback(
#     Output("notificacoes", "children"),
#     Input("btn-criar-av", "n_clicks"),
#     State("empresa-novo-av", "value"),
#     State('descricao-novo-av', 'value'),
#     State("usuarios-av", "selectedRows"),
#     prevent_initial_call=True,
# )
# def criar_assessment(n, empresa: str, descricao: str, linhas: list[dict[str, str]]):
#     if not n:
#         raise PreventUpdate
#     elif not empresa:
#         NOTIFICACAO = dmc.Notification(
#             id="notificacao-criar-av",
#             title="Atenção",
#             message="Selecione uma empresa",
#             action="show",
#             color="red",
#         )
#     elif not linhas:
#         NOTIFICACAO = dmc.Notification(
#             id="notificacao-criar-av",
#             title="Atenção",
#             message="Selecione pelo menos um usuário",
#             action="show",
#             color="red",
#         )
#     else:
#         participantes = [ObjectId(linha["id"]) for linha in linhas]
#         try:
#             nova_aplicacao = AssessmentVendedor(
#                 empresa=ObjectId(empresa), participantes=participantes, descricao=descricao
#             )
#             nova_aplicacao.registrar()
#         except ValidationError as e:
#             erro = e.errors()[0]["ctx"]["error"]
#             NOTIFICACAO = dmc.Notification(
#                 id="notificacao-erro-criacao-av",
#                 title="Erro",
#                 message=str(erro),
#                 action="show",
#                 color="red",
#             )
#         else:
#             NOTIFICACAO = dmc.Notification(
#                 id="notificacao-sucesso-criacao-av",
#                 title="Pronto!",
#                 message="O Assessment Vendedor foi criado com sucesso",
#                 action="show",
#                 color="green",
#             )

#     return NOTIFICACAO

# @callback(
#     Output("notificacoes", "children"),
#     Input("btn-salvar-av", "n_clicks"),
#     State('usuarios-av', 'selectedRows'),
#     State('descricao-novo-av', 'value'),
#     State('url', 'search')
# )
# def atualizar_assessment(n: int, linhas: list[dict[str, str]], descricao: str, search: str):
#     if not n:
#         raise PreventUpdate
#     elif not linhas:
#         NOTIFICACAO = dmc.Notification(
#             id="notificacao-salvar-av",
#             title="Atenção",
#             message="Selecione pelo menos um assessment vendedor",
#             action="show",
#             color="red",
#         )
#     else:
#         id = parse_qs(search[1:]).get('id', [None])[0]
