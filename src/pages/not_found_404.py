from dash import html, register_page
import dash_mantine_components as dmc

register_page(__name__, title="Página não encontrada")

layout = dmc.Text("Esta página não existe")
