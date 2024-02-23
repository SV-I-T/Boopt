import base64
import io

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html, no_update, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from utils.banco_dados import db
from utils.modelo_usuario import NovosUsuariosBatelada, checar_login

from .usuarios import CARGOS_PADROES

register_page(__name__, path="/admin/usuarios/batelada", title="Cadastro em Massa")


@checar_login
def layout():
    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in db("Boopt", "Empresas").find(
            projection={"_id": 1, "nome": 1}, sort={"nome": 1}
        )
    ]
    return [
        dmc.Title("Cadastro em massa", order=1, weight=700),
        dmc.Select(
            id="empresa-usr-massa",
            label="Empresa de cadastro",
            icon=DashIconify(icon="fluent:building-24-filled", width=24),
            name="empresa",
            data=data_empresas,
            required=True,
            searchable=True,
            nothingFound="Não encontrei nada",
            w=300,
        ),
        dcc.Upload(
            id="upload-cadastro-massa",
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            children=dmc.Button(
                id="usr-massa-upload",
                children="Escolha o arquivo (.xlsx)",
                leftIcon=DashIconify(icon="fluent:arrow-upload-16-filled", width=24),
            ),
        ),
        dmc.Text(id="usr-massa-arquivo", children="Nenhum arquivo escolhido"),
        dmc.Button(
            id="usr-massa-download-template",
            children="Baixar modelo (.xlsx)",
            variant="subtle",
            compact=True,
            leftIcon=DashIconify(icon="fluent:arrow-download-16-filled", width=16),
        ),
        html.Div(id="feedback-usr-massa"),
    ]


@callback(
    Output("download", "data", allow_duplicate=True),
    Input("usr-massa-download-template", "n_clicks"),
    prevent_initial_call=True,
)
def baixar_template_cadastro_massa(n):
    if not n:
        raise PreventUpdate

    buffer = io.BytesIO()
    wb = NovosUsuariosBatelada.gerar_modelo(cargos_padres=CARGOS_PADROES)
    wb.save(buffer)
    wb.close()
    return dcc.send_bytes(
        src=buffer.getvalue(),
        filename="template_cadastro.xlsx",
        type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@callback(
    Output("usr-massa-arquivo", "children"),
    Output("feedback-usr-massa", "children"),
    Output("notificacoes", "children"),
    Input("upload-cadastro-massa", "contents"),
    State("upload-cadastro-massa", "filename"),
    prevent_initial_call=True,
)
def carregar_arquivo_xlsx(contents: str, nome: str):
    if not contents:
        raise PreventUpdate
    ARQUIVO = nome if nome else "Nenhum arquivo escolhido"

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    NovosUsuariosBatelada.carregar_planilha(io.BytesIO(decoded))

    ALERTA = no_update
    NOTIFICACAO = no_update

    return ARQUIVO, ALERTA, NOTIFICACAO
