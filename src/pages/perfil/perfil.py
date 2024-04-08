from datetime import datetime

import dash_mantine_components as dmc
from dash import html, register_page
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Usuario, checar_perfil

register_page(__name__, path="/app/perfil", title="Meu perfil")


@checar_perfil
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
                        dmc.TextInput(
                            label="Nome completo",
                            value=f"{usr.nome} {usr.sobrenome}",
                            disabled=True,
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
                        {"maxWidth": 567, "co ls": 1},
                    ],
                    children=[
                        dmc.TextInput(
                            label="Empresa",
                            value=db("Boopt", "Empresas").find_one(
                                {"_id": usr.empresa}, {"nome": 1, "_id": 0}
                            )["nome"],
                            disabled=True,
                        ),
                        dmc.TextInput(label="Cargo", value=usr.cargo, disabled=True),
                        dmc.TextInput(
                            label="Perfil",
                            value=usr.perfil.name.capitalize(),
                            disabled=True,
                        ),
                    ],
                ),
                dmc.Divider(),
                dmc.Title("Segurança", className="secao-pagina"),
                html.Div("vc só pode alterar blablabla"),
                dmc.PasswordInput(id="senha-atual", label="Digite sua senha atual"),
                dmc.Divider(m="1rem"),
                dmc.PasswordInput(id="senha-nova", label="Digite sua nova senha"),
                dmc.PasswordInput(
                    id="senha-nova-check", label="Confirme sua nova senha"
                ),
                dmc.Button(
                    id="btn-alterar-senha", children="Alterar senha", fullWidth=True
                ),
                html.Div(id="feedback-alterar-senha"),
            ],
        ),
    ]
