import re

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

layout_cpf = dmc.Grid(
    [
        dmc.Col(
            dmc.TextInput(
                label="Insira seu CPF:",
                description="Somente números",
                type="text",
                placeholder="Ex: 12345678911",
                id="input-cpf",
            ),
            span="auto",
        ),
        dmc.Col(
            dmc.Button(
                "Enviar",
                leftIcon=DashIconify(icon="majesticons:send"),
                # size="lg",
                # variant="filled",
                # color="theme.colors.primaryShade",
                id="btn-submit-cpf",
            ),
            span="content",
        ),
    ],
    grow=True,
    align="flex-end",
)


@callback(
    Output("url", "search"),
    Output("input-cpf", "error"),
    Input("btn-submit-cpf", "n_clicks"),
    State("input-cpf", "value"),
    State("url", "search"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def entrar_cpf(n, cpf, search, path: str):
    if not n:
        raise PreventUpdate
    if (len(cpf) != 11) or (not str.isnumeric(cpf)):
        return no_update, "CPF inválido"
    id = re.findall(r"id=([a-zA-Z0-9]*)\&?", search)
    if path.startswith("/resultados") or not id:
        return f"cpf={cpf}", no_update
    else:
        return f"id={id[0]}&cpf={cpf}", no_update
