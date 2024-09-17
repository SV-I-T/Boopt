from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    clientside_callback,
    html,
    register_page,
)
from dash_player import DashPlayer

from utils.video import video_teste

register_page(__name__, path_template="/app/vela/videos/<id_video>")


def layout(id_video: str):
    return DashPlayer(
        id=f"vela-v{video_teste.vid}",
        url=video_teste.url,
        controls=True,
        intervalCurrentTime=1000,
    )


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="atualizar_infos_player"),
    Output("vela-player-progress", "children"),
    Input("vela-player", "currentTime"),
    State("vela-player", "duration"),
)
