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
    get_asset_url,
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from openpyxl.worksheet.datavalidation import DataValidation
from utils.banco_dados import mongo

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


def gerar_template_cadastro():
    caminho = get_asset_url("modelo_novos_usuarios.xlsx")
    wb = openpyxl.load_workbook(caminho)
    ws = wb["Plan1"]
    rule = DataValidation(
        type="list",
        formula1=f'"{",".join(CARGOS_PADROES)}"',
        allow_blank=True,
        showErrorMessage=False,
    )
    ws.add_data_validation(rule)
    rule.add("F2")
    wb.save(caminho)
    wb.close()


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
                data=sorted(CARGOS_PADROES),
                creatable=True,
                clearable=False,
                searchable=True,
                icon=DashIconify(icon="fluent:person-wrench-20-filled", width=24),
                name="cargo",
            ),
            dmc.Button(id="btn-criar-novo-usr", children="Criar"),
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
                    dmc.Button(
                        id="usr-massa-upload",
                        children="Escolha o arquivo",
                        leftIcon=DashIconify(
                            icon="fluent:arrow-upload-16-filled", width=24
                        ),
                    ),
                    dmc.Text(
                        id="usr-massa-arquivo", children="Nenhum arquivo escolhido"
                    ),
                ]
            ),
            dmc.Button(
                id="usr-massa-download-template",
                children="Baixar modelo XLSX",
                variant="subtle",
                compact=True,
                leftIcon=DashIconify(icon="fluent:arrow-download-16-filled", width=24),
            ),
        ],
    )


def layout():
    return [
        dmc.Group(
            [
                dmc.Button(
                    id="btn-modal-novo-usr",
                    children="Novo Usuário",
                    leftIcon=DashIconify(icon="fluent:add-12-filled", width=24),
                ),
                dmc.Button(
                    id="btn-modal-usr-massa",
                    children="Cadastro em massa",
                    variant="outline",
                ),
            ]
        ),
        modal_novo_usr(),
        modal_novo_usr_massa(),
        dmc.Text("Gerenciamento de usuários", size="xl", weight=700),
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
    ClientsideFunction(namespace="clientside", function_name="abrir_modal_novo_usr"),
    Output("modal-novo-usr", "opened"),
    Input("btn-modal-novo-usr", "n_clicks"),
)

clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="abrir_modal_novo_usr"),
    Output("modal-usr-massa", "opened"),
    Input("btn-modal-usr-massa", "n_clicks"),
)


@callback(
    Output("notificacoes", "children"),
    Output("modal-novo-usr", "opened", allow_duplicate=True),
    Input("btn-criar-novo-usr", "n_clicks"),
    State("nome-novo-usr", "value"),
    State("sobrenome-novo-usr", "value"),
    State("cpf-novo-usr", "value"),
    State("data-novo-usr", "value"),
    State("email-novo-usr", "value"),
    State("cargo-novo-usr", "value"),
    prevent_initial_call=True,
)
def criar_novo_usr(
    n, nome: str, sobrenome: str, cpf: str, data: str, email: str, cargo: str
):
    print(get_asset_url("modelo_novos_usuarios.xlsx"))
    if not n:
        raise PreventUpdate
    return dmc.Notification(
        id="notificacao-novo-usr-suc",
        title="Sucesso!",
        message=f"O usuário '{nome}', de CPF '{cpf}' foi criado com sucesso.",
        color="green",
        action="show",
    ), False
