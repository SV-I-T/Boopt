import dash_mantine_components as dmc
from dash import html, register_page

register_page(__name__, path="/", title="DEMO | Vela Assessment")


def layout():
    return [
        html.H1("Oi", className="titulo-pagina"),
        html.Form(
            action="/test",
            style={"display": "flex", "flex-direction": "column", "gap": "1rem"},
            children=[
                dmc.TextInput(type="text", placeholder="Nome", name="nome"),
                dmc.TextInput(type="text", placeholder="Empresa", name="empresa"),
                dmc.TextInput(type="text", placeholder="Cargo", name="cargo"),
                dmc.TextInput(type="text", placeholder="Telefone", name="telefone"),
                dmc.TextInput(type="text", placeholder="Email", name="email"),
                dmc.Button(children="Começar teste", type="submit"),
            ],
        ),
    ]
