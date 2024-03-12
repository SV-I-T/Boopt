from datetime import datetime

import dash_mantine_components as dmc
from dash import (
    Input,
    Output,
    State,
    callback,
    dcc,
    get_asset_url,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask import request
from flask_login import current_user, login_user
from utils.modelo_usuario import Usuario

# register_page(__name__, path_template="/login/<next>", title="Entrar")


def layout(next: str = None):
    if current_user.is_authenticated:
        return [
            dmc.Title(children="Você já está logado!", order=1),
            dmc.Anchor(
                children="Clique aqui para ir ao seu dashboard",
                href="/usuario/dashboard",
                underline=True,
            ),
        ]
    return dmc.Group(
        [
            dcc.Store(id="next-url", data=next),
            html.Div(
                id="login-side-rect",
                children=html.Img(
                    src=get_asset_url("imgs/boopt/horizontal_branco.svg")
                ),
            ),
            dmc.Container(
                children=dmc.Stack(
                    miw=300,
                    children=[
                        html.Div(
                            [
                                dmc.Title("LOGIN", size=40, weight=500),
                                dmc.HoverCard(
                                    radius="md",
                                    shadow="md",
                                    width=200,
                                    children=[
                                        dmc.HoverCardTarget(
                                            dmc.Text(
                                                "Primeira vez?",
                                                color="dimmed",
                                                size="sm",
                                            )
                                        ),
                                        dmc.HoverCardDropdown(
                                            children=[
                                                dmc.Text(
                                                    size="sm",
                                                    children="Por padrão, sua senha é a sua data de nascimento no formato DDMMAAAA.",
                                                ),
                                                dmc.Text(
                                                    size="sm",
                                                    children=f'Exemplo: {datetime.today().strftime("%d%m%Y")}.',
                                                    weight=700,
                                                ),
                                                dmc.Text(
                                                    size="sm",
                                                    children="Não se esqueça de trocar uma mais segura depois.",
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        dmc.TextInput(
                            id="login-usr",
                            label=dmc.Text(
                                "CPF ou E-mail", size=26, weight=300, color="#5C5C5C"
                            ),
                            type="login",
                            icon=DashIconify(icon="fluent:person-20-filled", width=20),
                        ),
                        dmc.PasswordInput(
                            id="login-senha",
                            label=dmc.Text(
                                "Senha", size=26, weight=300, color="#5C5C5C"
                            ),
                            icon=DashIconify(icon="fluent:key-20-filled", width=20),
                            name="password",
                        ),
                        dmc.Group(
                            grow=True,
                            children=[
                                dmc.Checkbox(
                                    id="login-check-lembrar",
                                    label="Lembrar de mim",
                                    checked=False,
                                ),
                                dmc.Anchor(
                                    href="/reset",
                                    children="Esqueci minha senha",
                                    underline=False,
                                    size="sm",
                                    w="fit-content",
                                ),
                            ],
                        ),
                        dmc.Button(
                            id="login-btn",
                            children=dmc.Text("Entrar", size=26, weight=400),
                            variant="gradient",
                            fullWidth=True,
                            h=40,
                        ),
                    ],
                ),
            ),
        ]
    )


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("notificacoes", "children", allow_duplicate=True),
    Output("login-data", "data"),
    Input("login-btn", "n_clicks"),
    State("login-usr", "value"),
    State("login-senha", "value"),
    State("login-check-lembrar", "checked"),
    State("next-url", "data"),
    prevent_initial_call=True,
)
def logar(n, login, senha, lembrar, next_url):
    if not n:
        raise PreventUpdate
    identificador = "email" if "@" in login else "cpf"
    try:
        usr = Usuario.buscar(identificador=identificador, valor=login)
        usr.validar_senha(senha)
    except AssertionError as e:
        URL = no_update
        NOTIFICACAO = dmc.Notification(
            id="notificacao-erro-login",
            title="Atenção",
            message=str(e),
            color="red",
            action="show",
        )
        LOGIN_DATA = no_update
    else:
        login_user(usr, remember=lembrar, force=True)
        URL = f"{next_url}" if next_url else "/"
        NOTIFICACAO = no_update
        LOGIN_DATA = 1

    return URL, NOTIFICACAO, LOGIN_DATA
