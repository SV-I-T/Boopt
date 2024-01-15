from dash import html, dcc, Output, Input, State, callback, no_update, register_page
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

from utils.login import Usuario

register_page(__name__, path="/login")


def layout(next: str = None):
    return html.Div(
        [
            dcc.Store(id="login-next-store", data=next),
            dmc.Card(
                [
                    dmc.CardSection(dmc.Text("Login")),
                    dmc.CardSection(
                        [
                            dmc.TextInput(
                                label="CPF", id="login-cpf-input", type="text"
                            ),
                            dmc.TextInput(
                                label="Senha", id="login-senha-input", type="password"
                            ),
                            dmc.Checkbox(
                                label="Lembrar de mim",
                                id="login-lembrar-check",
                                disabled=True,
                            ),
                            dmc.Button("Entrar", id="login-entrar-btn"),
                            html.Div(id="login-feedback"),
                        ]
                    ),
                ]
            ),
        ]
    )


@callback(
    Output("login-feedback", "children"),
    Input("login-entrar-btn", "n_clicks"),
    State("login-cpf-input", "value"),
    State("login-senha-input", "value"),
    State("login-lembrar-check", "disabled"),
    State("login-next-store", "data"),
)
def entrar(n, cpf: str, senha: str, lembrar: bool, next: str):
    pass
