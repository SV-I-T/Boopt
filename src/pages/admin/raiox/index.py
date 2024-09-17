import dash_mantine_components as dmc
from dash import html, register_page
from dash_iconify import DashIconify

from utils.login import checar_perfil
from utils.usuario import Role, Usuario

register_page(__name__, title="Raio-X", path="/app/admin/raiox")

MAX_PAGINA = 10


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM, Role.GEST))
def layout():
    usr = Usuario.atual()
    if usr.role == Role.ADM:
        data_empresas = [str(usr.empresa)]
    else:
        data_empresas = usr.consultar_empresas()

    return [
        html.H1("Raio-X"),
        dmc.Stack(
            [
                dmc.Group(
                    position="right",
                    children=[
                        dmc.Select(
                            id="empresa-vela",
                            icon=DashIconify(
                                icon="fluent:building-24-regular", width=24
                            ),
                            name="empresa",
                            data=data_empresas,
                            required=True,
                            searchable=True,
                            nothingFound="Não encontramos nada",
                            placeholder="Selecione uma empresa",
                            w=250,
                            mr="auto",
                            value=str(usr.empresa),
                            display="none"
                            if usr.role in (Role.ADM, Role.GEST)
                            else "block",
                        ),
                        dmc.Anchor(
                            href="/app/admin/entregas/dashboard",
                            children=dmc.Button(
                                children="Resultados",
                                leftIcon=DashIconify(
                                    icon="fluent:chart-multiple-24-regular", width=24
                                ),
                            ),
                        ),
                        dmc.Anchor(
                            id="a-nova-entrega",
                            href="/app/admin/entregas/new",
                            children=dmc.Button(
                                children="Nova missão",
                                leftIcon=DashIconify(
                                    icon="fluent:add-24-regular", width=24
                                ),
                                variant="gradient",
                            ),
                        )
                        if usr.role != Role.GEST
                        else None,
                    ],
                ),
                dmc.Table(
                    striped=True,
                    highlightOnHover=True,
                    withBorder=True,
                    withColumnBorders=True,
                    style={"width": "100%"},
                    children=[
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("Descrição"),
                                    html.Th("Fase", style={"width": 120}),
                                    html.Th("Criado em", style={"width": 100}),
                                    html.Th("Adesão", style={"width": 100}),
                                    html.Th("Prazo", style={"width": 120}),
                                    html.Th("Ações", style={"width": 150}),
                                ]
                            )
                        ),
                        html.Tbody(
                            id="table-vela-body",
                            children=[],
                        ),
                    ],
                ),
                dmc.Pagination(id="table-vela-nav", total=1, page=1, radius="xl"),
            ]
        ),
    ]
