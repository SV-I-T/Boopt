import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    clientside_callback,
    html,
    register_page,
)

register_page(__name__, path="/", title="DEMO | Vela Assessment")


def layout():
    return [
        html.H1("Oi", className="titulo-pagina"),
        html.Div(
            style={"display": "flex", "flex-direction": "column", "gap": "1rem"},
            children=[
                dmc.TextInput(type="text", placeholder="Nome", id="input-nome"),
                dmc.TextInput(type="text", placeholder="Empresa", id="input-empresa"),
                dmc.TextInput(type="text", placeholder="Cargo", id="input-cargo"),
                dmc.TextInput(type="text", placeholder="Telefone", id="input-telefone"),
                dmc.TextInput(type="text", placeholder="Email", id="input-email"),
                dmc.Button(id="btn-comecar-vela", children="Começar teste"),
            ],
        ),
    ]


clientside_callback(
    ClientsideFunction("clientside", "comecar_vela"),
    Output("url", "href"),
    Output("user-data", "data"),
    Input("btn-comecar-vela", "n_clicks"),
    State("input-nome", "value"),
    State("input-empresa", "value"),
    State("input-cargo", "value"),
    State("input-telefone", "value"),
    State("input-email", "value"),
    prevent_initial_call=True,
)
