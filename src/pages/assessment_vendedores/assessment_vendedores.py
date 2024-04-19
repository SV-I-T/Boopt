import dash_mantine_components as dmc
from dash import dcc, html, register_page
from dash_iconify import DashIconify
from flask_login import current_user
from utils.modelo_assessment import AssessmentVendedor
from utils.modelo_usuario import Usuario, checar_perfil

register_page(
    __name__,
    path="/app/assessment-vendedor",
    title="Assessment Vendedor",
    redirect_from=["/app/dashboard"],
)


@checar_perfil
def layout():
    usr_atual: Usuario = current_user

    r = AssessmentVendedor.testes_disponiveis(usr_atual.id_)
    ultima_aplicacao = r["ultima_aplicacao"] if r else None
    ultima_resposta_id = r["ultima_resposta_id"] if r else None

    return html.Div(
        className="center-container",
        children=[
            dmc.Image(
                mb="1rem",
                width=500,
                height=200,
                withPlaceholder=True,
                alt="Logo Assessment",
                placeholder=dmc.Text("LOGO"),
            ),
            dmc.Text(
                "Te damos as boas-vindas ao Assessment de Vendedor Boopt.",
                weight=500,
                align="center",
                mb="4rem",
            ),
            dmc.Group(
                mb="4rem",
                children=[
                    dmc.Anchor(
                        dmc.Button(
                            children="Começar o teste"
                            if ultima_aplicacao and not ultima_aplicacao.get("resposta")
                            else "Sem teste disponível",
                            disabled=not (
                                ultima_aplicacao
                                and not ultima_aplicacao.get("resposta")
                            ),
                        ),
                        href=f"/app/assessment-vendedor/teste/?id={ultima_aplicacao['id']}"
                        if ultima_aplicacao and not ultima_aplicacao.get("resposta")
                        else None,
                    ),
                    dmc.Anchor(
                        dmc.Button(
                            children="Ver resultado",
                            disabled=not ultima_resposta_id,
                            color="BooptLaranja",
                        ),
                        href=f"/app/assessment-vendedor/resultado/?usr={usr_atual.id}&resposta={ultima_resposta_id}"
                        if ultima_resposta_id
                        else None,
                    ),
                ],
            ),
            html.Div(
                className="card card-videos-av",
                children=dmc.Group(
                    spacing="xl",
                    children=[
                        DashIconify(
                            icon="fluent:play-48-filled",
                            color="#fff",
                            className="play-videos-av",
                        ),
                        html.Div(
                            children=[
                                dcc.Markdown(
                                    "Acesse a nossa plataforma de vídeos **após realizar o teste do Assessment Boopt**"
                                ),
                                dmc.Anchor(
                                    href="",
                                    children=dmc.Button(
                                        children="Acessar",
                                        leftIcon=DashIconify(
                                            icon="fluent:filmstrip-play-16-regular",
                                            width=16,
                                        ),
                                        className="btn-borda-gradiente",
                                        disabled=not ultima_resposta_id,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
