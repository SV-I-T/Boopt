import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    clientside_callback,
    dcc,
    html,
    register_page,
)
from dash_player import DashPlayer

register_page(__name__, path="/app/vela/videos", title="Vela - Videos")


def layout():
    return [
        DashPlayer(
            id="vela-player",
            url="https://vimeo.com/908405972",
            controls=True,
            intervalCurrentTime=1000,
        ),
        html.P(id="vela-player-progress"),
    ]


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="atualizar_infos_player"),
    Output("vela-player-progress", "children"),
    Input("vela-player", "currentTime"),
    State("vela-player", "duration"),
)
