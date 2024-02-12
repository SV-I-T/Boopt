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
from flask import url_for
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from pydantic import ValidationError
from utils.modelo_usuario import NovoUsuario

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


def modal_novo_usr():
    return dmc.Modal(
        title=dmc.Title("Novo Usuário", weight=600, order=2),
        id="modal-novo-usr",
        zIndex=100000,
        size=600,
        children=[
            dmc.Group(
                grow=True,
                children=[
                    dmc.TextInput(
                        id="nome-novo-usr",
                        label="Primeiro Nome",
                        type="text",
                        required=True,
                        icon=DashIconify(icon="fluent:person-12-filled", width=24),
                        name="nome",
                    ),
                    dmc.TextInput(
                        id="sobrenome-novo-usr",
                        label="Sobrenome",
                        type="text",
                        required=True,
                        name="sobrenome",
                    ),
                ],
            ),
            dmc.Group(
                grow=True,
                children=[
                    dmc.TextInput(
                        id="cpf-novo-usr",
                        label="CPF",
                        type="number",
                        required=True,
                        description="Somente números",
                        placeholder="12345678910",
                        icon=DashIconify(icon="tabler:numbers", width=24),
                        name="cpf",
                    ),
                    dmc.DatePicker(
                        id="data-novo-usr",
                        label="Data de Nascimento",
                        required=True,
                        description="Será a senha do usuário",
                        locale="pt-br",
                        inputFormat="DD [de] MMMM [de] YYYY",
                        firstDayOfWeek="sunday",
                        initialLevel="year",
                        clearable=False,
                        placeholder=datetime.now().strftime(r"%d de %B de %Y"),
                        icon=DashIconify(
                            icon="fluent:calendar-date-20-filled", width=24
                        ),
                        name="data",
                    ),
                ],
            ),
            dmc.TextInput(
                id="email-novo-usr",
                label="E-mail",
                type="email",
                description="(Opcional)",
                placeholder="nome@dominio.com",
                icon=DashIconify(icon="fluent:mail-12-filled", width=24),
                name="email",
            ),
            dmc.Select(
                id="cargo-novo-usr",
                label="Cargo/Função",
                required=True,
                description="Selecione a opção que melhor se encaixa ao cargo",
                data=CARGOS_PADROES,
                creatable=True,
                clearable=False,
                searchable=True,
                icon=DashIconify(icon="fluent:person-wrench-20-filled", width=24),
                name="cargo",
            ),
            dmc.Checkbox(
                id="recruta-novo-usr",
                label="Seleção e Recrutamento",
                checked=False,
            ),
            dmc.Button(id="btn-criar-novo-usr", children="Criar"),
            html.Div(id="error-container-novo-usr"),
        ],
    )


def modal_novo_usr_massa():
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


def layout(empresa: str = "Empresa"):
    return [
        dmc.Title("Gerenciamento de usuários", order=1, weight=700),
        dmc.Title(id="text-empresa", children=empresa, order=3, weight=500),
        dmc.ButtonGroup(
            [
                dmc.Button(
                    id="btn-modal-novo-usr",
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
        modal_novo_usr(),
        modal_novo_usr_massa(),
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
    ClientsideFunction(namespace="clientside", function_name="abrir_modal"),
    Output("modal-novo-usr", "opened"),
    Input("btn-modal-novo-usr", "n_clicks"),
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


@callback(
    Output("notificacoes", "children"),
    Output("modal-novo-usr", "opened", allow_duplicate=True),
    Output("error-container-novo-usr", "children"),
    Input("btn-criar-novo-usr", "n_clicks"),
    State("nome-novo-usr", "value"),
    State("sobrenome-novo-usr", "value"),
    State("cpf-novo-usr", "value"),
    State("data-novo-usr", "value"),
    State("email-novo-usr", "value"),
    State("cargo-novo-usr", "value"),
    State("recruta-novo-usr", "checked"),
    State("text-empresa", "children"),
    prevent_initial_call=True,
)
def criar_novo_usr(
    n,
    nome: str,
    sobrenome: str,
    cpf: str,
    data: str,
    email: str,
    cargo: str,
    recruta: bool,
    empresa: str,
):
    if not n:
        raise PreventUpdate

    try:
        usr = NovoUsuario(
            nome=nome,
            sobrenome=sobrenome,
            cpf=cpf,
            data=data,
            email=email,
            cargo=cargo,
            recruta=recruta,
            empresa=empresa,
        )
        usr.registrar()

    except ValidationError as e:
        print(e)
        erro = e.errors()[0]["ctx"]["error"]
        return no_update, no_update, dmc.Alert(str(erro), color="red", variant="filled")

    except AssertionError as e:
        return no_update, no_update, dmc.Alert(
            color="red",
            variant="filled",
            mt="1rem",
            children=str(e),
        )

    return dmc.Notification(
        id="notificacao-novo-usr-suc",
        title="Sucesso!",
        message=[
            dmc.Text(span=True, children="O usuário "),
            dmc.Text(span=True, children=nome, weight=700),
            dmc.Text(span=True, children=" foi criado com sucesso."),
        ],
        color="green",
        action="show",
    ), False, no_update
