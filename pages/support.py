import dash_mantine_components as dmc
from dash import dcc, html, register_page

register_page(__name__, path="/app/support", title="Suporte")


def layout():
    return [
        html.H1("Suporte"),
        dcc.Markdown(
            children="""
            Encontrou algum problema? Tem alguma sugestão? Contate-nos através de [suporte@boopt.com.br](mailto:suporte@boopt.com.br?subject=Teste&body=Corpo%20do%20texto).""",
        ),
    ]
