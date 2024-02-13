import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask_login import current_user, login_user
from utils.modelo_usuario import Usuario

register_page(__name__, path="/login", title="Entrar")


def layout():
    if current_user.is_authenticated:
        return [
            dmc.Title(children="Você já está logado!", order=1),
            dmc.Anchor(
                children="Clique aqui para ir ao seu dashboard",
                href="/usuario/dashboard",
                underline=True,
            ),
        ]
    return dmc.Container(
        maw=300,
        children=[
            dmc.TextInput(
                id="login-usr",
                label="CPF ou E-mail",
                type="login",
                icon=DashIconify(icon="fluent:person-12-filled", width=24),
            ),
            dmc.PasswordInput(
                id="login-senha",
                label="Senha",
                icon=DashIconify(icon="fluent:password-16-filled", width=24),
                name="password",
            ),
            dmc.Checkbox(
                id="login-check-lembrar", label="Lembrar de mim", checked=False
            ),
            dmc.Anchor(href="/reset", children="Esqueci minha senha", underline=True),
            dmc.Button(
                id="login-btn",
                children="Entrar",
                variant="gradient",
                size="lg",
                fullWidth=True,
            ),
            html.Div(id="login-feedback"),
        ],
    )


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("login-feedback", "children"),
    Output("login-data", "data"),
    Input("login-btn", "n_clicks"),
    State("login-usr", "value"),
    State("login-senha", "value"),
    State("login-check-lembrar", "checked"),
    State("login-data", "data"),
    prevent_initial_call=True,
)
def logar(n, login, senha, lembrar, login_data):
    if not n:
        raise PreventUpdate
    identificador = "email" if "@" in login else "cpf"
    try:
        usr = Usuario.buscar(identificador=identificador, valor=login, senha=senha)
    except AssertionError as e:
        return no_update, dmc.Alert(
            "Verifique as suas credenciais e tente novamente.",
            color="red",
            title=str(e),
        ), no_update

    login_user(usr, remember=lembrar, force=True)
    return "/usuario/dashboard", no_update, login_data + 1
