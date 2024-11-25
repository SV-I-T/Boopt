import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    clientside_callback,
    dcc,
    get_asset_url,
    html,
    register_page,
)

from utils.video import video_teste

register_page(__name__, path="/app/vela/videos", title="Vela - Videos")


def layout():
    return [
        html.H1(
            [
                dcc.Link("", href="/app/vela", title="Voltar"),
                "Vídeos",
                html.Img(src=get_asset_url("assets/vela/tag_ass.svg")),
            ]
        ),
        html.Div(
            className="video-gallery",
            children=[
                dcc.Link(
                    href=f"/app/vela/videos/{video_teste.id_}",
                    children=html.Div(
                        children=[
                            html.Div(
                                html.Img(src=video_teste.thumbnail_url),
                            ),
                            html.Span(video_teste.titulo),
                        ],
                    ),
                )
                for i in range(10)
            ],
        ),
    ]
