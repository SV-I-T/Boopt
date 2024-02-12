import dash_mantine_components as dmc
from dash import Input, Output, State, callback, register_page
from dash_iconify import DashIconify

register_page(__name__, path="/login", title="Entrar")


def layout():
    return dmc.Container(
        maw=300,
        children=[
            dmc.TextInput(
                id="usr-login",
                label="CPF ou E-mail",
                type="login",
                icon=DashIconify(icon="fluent:person-12-filled", width=24),
            ),
            dmc.PasswordInput(
                id="senha-login",
                label="Senha",
                icon=DashIconify(icon="fluent:password-16-filled", width=24),
            ),
            dmc.Checkbox(
                id="check-lembrar-login", label="Lembrar de mim", checked=False
            ),
            dmc.Anchor(href="/reset", children="Esqueci minha senha", underline=True),
            dmc.Button(
                id="btn-login-usr",
                children="Entrar",
                variant="gradient",
                size="lg",
                fullWidth=True,
            ),
        ],
    )
