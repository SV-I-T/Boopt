from datetime import datetime

import dash_mantine_components as dmc
from dash import html, register_page
from flask_login import current_user
from utils.modelo_usuario import Usuario, checar_login

register_page(__name__, path="/app/perfil", title="Meu perfil")


@checar_login
def layout():
    usr: Usuario = current_user
    return [
        dmc.Title("Meu perfil", className="titulo-pagina"),
        html.Div(
            className="editar-perfil",
            children=[
                dmc.Title("Informações Pessoais", className="secao-pagina"),
                dmc.SimpleGrid(
                    cols=2,
                    breakpoints=[
                        {"maxWidth": 567, "cols": 1},
                    ],
                    children=[
                        dmc.TextInput(label="Nome", value=usr.nome, disabled=True),
                        dmc.TextInput(
                            label="Sobrenome", value=usr.sobrenome, disabled=True
                        ),
                        dmc.TextInput(label="CPF", value=usr.cpf, disabled=True),
                        dmc.Group(
                            position="right",
                            grow=True,
                            children=[
                                dmc.TextInput(label="Email", value=usr.email),
                                dmc.Anchor("Editar", href="/app/perfil/alterar-email"),
                            ],
                        ),
                        dmc.TextInput(
                            label="Data de nascimento",
                            value=datetime.strptime(usr.data, "%Y-%m-%d").strftime(
                                "%d de %B de %Y"
                            ),
                            disabled=True,
                        ),
                    ],
                ),
                dmc.Divider(),
                dmc.Title("Informações Profissionais", className="secao-pagina"),
                dmc.SimpleGrid(
                    cols=2,
                    breakpoints=[
                        {"maxWidth": 567, "cols": 1},
                    ],
                    children=[
                        dmc.TextInput(
                            label="Empresa", value=usr.empresa_nome, disabled=True
                        ),
                        dmc.TextInput(label="Cargo", value=usr.cargo, disabled=True),
                        dmc.TextInput(
                            label="Gestor",
                            value=usr.gestor and "Sim" or "Não",
                            disabled=True,
                        ),
                        dmc.TextInput(
                            label="Candidato",
                            value=usr.recruta and "Sim" or "Não",
                            disabled=True,
                        ),
                    ],
                ),
                dmc.Divider(),
                dmc.Title("Segurança", className="secao-pagina"),
                dmc.Tooltip(
                    label="Você só pode alterar sua senha com um email registrado",
                    withArrow=True,
                    children=dmc.Anchor(
                        href="/app/perfil/alterar-senha",
                        children=dmc.Button(
                            "Alterar senha",
                            disabled=not usr.email,
                        ),
                    ),
                    disabled=usr.email,
                ),
            ],
        ),
    ]
