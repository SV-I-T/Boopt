import dash_mantine_components as dmc
from dash import html, register_page
from dash_iconify import DashIconify

register_page(__name__, path="/", title="DEMO | Vela Assessment")


def layout():
    return [
        html.Div(
            className="promo",
            children=[
                html.Img(
                    src="./assets/imgs/vela/vela mar.jpg",
                    alt="Barco",
                    className="barco",
                ),
                html.Img(
                    src="./assets/imgs/vela/tag_ass_inv.svg",
                    alt="Logo Vela",
                    className="logo-vela",
                ),
                html.P("Seja bem-vindo ao", className="welcome"),
            ],
        ),
        html.Div(
            className="slogan",
            children=[
                html.Span("Use o"),
                html.Span(" vento ", className="bold"),
                html.Span("ao"),
                html.Span(" seu favor ", className="bold"),
            ],
        ),
        html.Form(
            action="/test",
            className="form-infos-vela",
            children=[
                dmc.TextInput(
                    type="text",
                    placeholder="Nome",
                    name="nome",
                    icon=DashIconify(icon="fluent:person-20-regular", width=20),
                ),
                dmc.TextInput(
                    type="text",
                    placeholder="Empresa",
                    name="empresa",
                    icon=DashIconify(icon="fluent:building-20-regular", width=20),
                ),
                dmc.TextInput(
                    type="text",
                    placeholder="Cargo",
                    name="cargo",
                    icon=DashIconify(icon="fluent:person-wrench-20-regular", width=20),
                ),
                dmc.TextInput(
                    type="text",
                    placeholder="Telefone",
                    name="telefone",
                    icon=DashIconify(icon="fluent:phone-20-regular", width=20),
                ),
                dmc.TextInput(
                    type="text",
                    placeholder="Email",
                    name="email",
                    icon=DashIconify(icon="fluent:mention-20-filled", width=20),
                ),
                dmc.Button(
                    children="Quero fazer o teste",
                    type="submit",
                    classNames={"root": "btn-vela"},
                ),
            ],
        ),
    ]
