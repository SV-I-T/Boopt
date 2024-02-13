import dash_mantine_components as dmc
from components.alertas import criar_alerta
from dash import Input, Output, State, callback, html, register_page
from dash.exceptions import PreventUpdate
from flask_login import current_user
from utils.modelo_usuario import checar_login

register_page(__name__, path="/configuracoes/senha")


@checar_login
def layout():
    return dmc.Container(
        maw=300,
        children=[
            dmc.PasswordInput(id="senha-atual", label="Digite sua senha atual"),
            dmc.Divider(m="1rem"),
            dmc.PasswordInput(id="senha-nova", label="Digite sua nova senha"),
            dmc.PasswordInput(id="senha-nova-check", label="Confirme sua nova senha"),
            dmc.Button(
                id="btn-alterar-senha", children="Alterar senha", fullWidth=True
            ),
            html.Div(id="feedback-alterar-senha"),
        ],
    )


@callback(
    Output("feedback-alterar-senha", "children"),
    Input("btn-alterar-senha", "n_clicks"),
    State("senha-atual", "value"),
    State("senha-nova", "value"),
    State("senha-nova-check", "value"),
    prevent_initial_call=True,
)
def alterar_senha(n, atual, nova, nova_check):
    if not n:
        raise PreventUpdate
    try:
        current_user.alterar_senha(atual, nova, nova_check)
    except AssertionError as e:
        return criar_alerta(str(e), "red")
    return criar_alerta("Sua senha foi alterada com sucesso!", "green")
