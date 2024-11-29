from dash import dcc, get_asset_url, html, register_page

from utils import Role, Usuario, db
from utils.video import video_teste

register_page(__name__, path="/app/videos/vela", title="Biblioteca de Videos - Vela")


def layout():
    usr = Usuario.atual()

    resposta = db("VelaRespostas").find_one({"id_usuario": usr.id_}, {"_id": 1})

    if not resposta and usr.role in (Role.USR, Role.GEST):
        return html.H1(
            [
                "Vídeos",
                html.Img(src=get_asset_url("assets/vela/tag_ass.svg")),
            ],
            html.H2(
                "Você precisa primeiro ter um Assessment Vela completado para pode assistir aos vídeos."
            ),
        )

    return [
        html.H1(
            [
                "Vídeos",
                html.Img(src=get_asset_url("assets/vela/tag_ass.svg")),
            ]
        ),
        html.Div(
            className="video-gallery",
            children=[
                dcc.Link(
                    href=f"/app/videos/vela/{video_teste.id_}",
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
