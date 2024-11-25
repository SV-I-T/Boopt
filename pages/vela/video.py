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

from utils.video import Video

register_page(__name__, path_template="/app/vela/videos/<id_video>")


def layout(id_video: str):
    video = Video.consultar(id_video=id_video)

    return [
        html.H1([dcc.Link("", href="/app/vela/videos", title="Voltar"), video.titulo]),
        DashPlayer(
            id="vela-video",
            className="video-player",
            url=video.url,
            controls=True,
            intervalCurrentTime=1000,
            intervalDuration=10_000_000,
            intervalSecondsLoaded=10_000_000,
        ),
    ]


clientside_callback(
    ClientsideFunction(namespace="vela", function_name="atualizar_info_video"),
    Output("vela-video", "seekTo"),
    Input("vela-video", "currentTime"),
    State("vela-video", "url"),
    prevent_initial_update=True,
)
