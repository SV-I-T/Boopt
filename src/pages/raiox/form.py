import dash_mantine_components as dmc
from dash import (
    ALL,
    MATCH,
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    dcc,
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from icecream import ic

from utils.banco_dados import db
from utils.login import checar_perfil
from utils.raiox import RaioX
from utils.usuario import Role, Usuario

register_page(__name__, path="/app/raiox/form", title="Formulário - Raio-X")


@checar_perfil
def layout(v: int = 1):
    usr_atual = Usuario.atual()
    raiox = RaioX.ler_etapas(v)

    etapas = [
        dmc.AccordionItem(
            value=etapa.sigla,
            children=[
                dmc.AccordionControl(etapa.nome),
                dmc.AccordionPanel(
                    children=[
                        html.Div(
                            id={
                                "rx-passo": passo.id,
                                "comprou": str(passo.comprou),
                            },
                            children=[
                                passo.desc,
                                dmc.SegmentedControl(
                                    id=f"rx-{passo.id}",
                                    data=["Sim", "Não"],
                                    value=None,
                                    radius="xl",
                                ),
                            ],
                            **{
                                "data-hidden": True
                                if passo.comprou is not None
                                else False
                            },
                        )
                        for passo in etapa.passos
                    ]
                ),
            ],
        )
        for etapa in raiox.etapas
    ]

    if raiox.id_comprou:
        etapas.insert(
            raiox.id_comprou,
            dmc.SegmentedControl(
                data=[
                    {
                        "value": "1",
                        "label": "O cliente fechou a compra",
                    },
                    {
                        "value": "0",
                        "label": "O cliente NÃO fechou a compra",
                    },
                ],
                value=None,
                id="raiox-fechou",
            ),
        )

    vendedores = db("Usuários").find(
        {"empresa": usr_atual.empresa},
        {"_id": 0, "value": {"$toString": "$_id"}, "label": "$nome"},
    )

    return [
        html.H1("Raio-X"),
        html.H2("Informações de atendimento"),
        dmc.Select(
            id="raiox-vendedor",
            label="Vendedor",
            data=list(vendedores),
            searchable=True,
        ),
        html.H2("Etapas do atendimento"),
        dmc.Accordion(
            variant="separated",
            radius="xl",
            className="form-raiox",
            children=etapas,
        ),
        dmc.Button(id="raiox-enviar", children="Enviar"),
    ]


clientside_callback(
    ClientsideFunction("clientside", "alterar_passos_raiox_comprou"),
    Output({"rx-passo": ALL, "comprou": "True"}, "data-hidden"),
    Output({"rx-passo": ALL, "comprou": "False"}, "data-hidden"),
    Input("raiox-fechou", "value"),
    State({"rx-passo": ALL, "comprou": "True"}, "data-hidden"),
    State({"rx-passo": ALL, "comprou": "False"}, "data-hidden"),
    prevent_initial_call=True,
)
