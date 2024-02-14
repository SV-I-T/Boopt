import io
from datetime import datetime

import dash_mantine_components as dmc
import openpyxl
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    dcc,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from pydantic import ValidationError
from utils.modelo_usuario import NovoUsuario, checar_login

register_page(__name__, "/admin/usuarios", name="Gerenciamento de usuários")

CARGOS_PADROES = sorted(
    [
        "Vendedor",
        "Diretor Comercial",
        "Gerente de Loja",
        "Atendente",
        "Supervisor de Loja",
        "Regional",
    ]
)


def modal_cadastro_massa():
    return dmc.Modal(
        id="modal-usr-massa",
        title=dmc.Title("Cadastro em massa", weight=600, order=2),
        zIndex=10000,
        size=600,
        children=[
            dmc.Group(
                [
                    dcc.Upload(
                        id="upload-cadastro-massa",
                        accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        children=dmc.Button(
                            id="usr-massa-upload",
                            children="Escolha o arquivo (.xlsx)",
                            leftIcon=DashIconify(
                                icon="fluent:arrow-upload-16-filled", width=24
                            ),
                        ),
                    ),
                    dmc.Text(
                        id="usr-massa-arquivo", children="Nenhum arquivo escolhido"
                    ),
                ]
            ),
            dmc.Button(
                id="usr-massa-download-template",
                children="Baixar modelo (.xlsx)",
                variant="subtle",
                compact=True,
                leftIcon=DashIconify(icon="fluent:arrow-download-16-filled", width=16),
            ),
        ],
    )


@checar_login
def layout():
    return [
        dmc.Title("Gerenciamento de usuários", order=1, weight=700),
        dmc.ButtonGroup(
            [
                dmc.Button(
                    id="btn-novo-usr",
                    children="Novo Usuário",
                    leftIcon=DashIconify(icon="fluent:add-12-filled", width=24),
                    variant="gradient",
                ),
                dmc.Button(
                    id="btn-modal-usr-massa",
                    children="Cadastro em massa",
                    variant="light",
                ),
            ]
        ),
        modal_cadastro_massa(),
        dmc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Usuário"),
                            html.Th("Empresa"),
                            html.Th("Cargo"),
                            html.Th("Ações"),
                        ]
                    )
                ),
                html.Tbody(id="tab-g-usuarios-body"),
            ]
        ),
    ]


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="redirect_usuarios_edit"),
    Output("url", "pathname"),
    Input("btn-novo-usr", "n_clicks"),
)

clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="abrir_modal"),
    Output("modal-usr-massa", "opened"),
    Input("btn-modal-usr-massa", "n_clicks"),
)


@callback(
    Output("download", "data", allow_duplicate=True),
    Input("usr-massa-download-template", "n_clicks"),
    prevent_initial_call=True,
)
def baixar_template_cadastro_massa(n):
    if not n:
        raise PreventUpdate
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cadastro"
    ws.append(
        [
            "Primeiro Nome",
            "Sobrenome",
            "CPF",
            "Data de Nascimento",
            "Email",
            "Cargo/Função",
        ]
    )
    ws.column_dimensions["C"].number_format = "@"
    ws.column_dimensions["D"].number_format = "DD/MM/YYYY"
    for col in ("A", "B", "E"):
        ws.column_dimensions[col].width = 32
    for col in ("C", "D", "F"):
        ws.column_dimensions[col].width = 16

    tabela = Table(
        displayName="Usuarios",
        ref="A1:F2",
        tableStyleInfo=TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
        ),
    )

    val_cargos = DataValidation(
        type="list",
        formula1=f'"{",".join(CARGOS_PADROES)}"',
        allow_blank=True,
        showErrorMessage=False,
    )

    ws.add_table(tabela)
    ws.add_data_validation(val_cargos)
    val_cargos.add("F2")

    buffer = io.BytesIO()
    wb.save(buffer)
    return dcc.send_bytes(
        src=buffer.getvalue(),
        filename="template_cadastro.xlsx",
        type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
