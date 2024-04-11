import dash_mantine_components as dmc
from dash import register_page, html
from utils.modelo_usuario import Perfil, Usuario, checar_perfil
from utils.modelo_assessment import AssessmentVendedor
from utils.banco_dados import db
from bson import ObjectId
from flask_login import current_user
import polars as pl

register_page(
    __name__,
    path="/app/admin/assessment-vendedor/view",
    title="Visualizar Assessment Vendedor",
)


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout(id: str = None):
    usr: Usuario = current_user

    assessment = AssessmentVendedor(
        **db("AssessmentVendedores", "Aplicações").find_one(
            {"_id": ObjectId(id), "empresa": usr.empresa}
        )
    )

    if not assessment:
        return [
            dmc.Title("Assessment inexistente", className="titulo-pagina"),
        ]

    respostas_aplicacao: pl.DataFrame = baixar_respostas_aplicacao(id)

    return [
        dmc.Title("Visualizar Assessment Vendedor", className="titulo-pagina"),
        dmc.Title(
            f'{assessment.descricao} ({assessment.id_.generation_time.strftime("%d/%m/%Y")})',
            className="secao-pagina",
        ),
        dmc.Table(
            id="tabela-respostas-aplicacao",
            striped=True,
            highlightOnHover=True,
            withBorder=True,
            withColumnBorders=True,
            style={"width": "100%"},
            children=[
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Nome"),
                            html.Th("Data de envio"),
                            html.Th("Pontos"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(row["nome"]),
                                html.Td(
                                    row["_id"].generation_time.strftime(
                                        "%d/%m/%Y %H:%M"
                                    )
                                    if row["_id"]
                                    else "--"
                                ),
                                html.Td(
                                    dmc.Anchor(
                                        children=f'{row["nota"]:.1f}',
                                        href=f'/app/assessment-vendedor/resultado/?usr={usr.id}&resposta={row["_id"]}',
                                    )
                                    if row["nota"]
                                    else "--"
                                ),
                            ]
                        )
                        for row in respostas_aplicacao.to_dicts()
                    ]
                ),
            ],
        ),
    ]


def baixar_respostas_aplicacao(id_aplicacao: str) -> pl.DataFrame:
    r = (
        db("AssessmentVendedores", "Aplicações").aggregate(
            [
                {"$match": {"_id": ObjectId(id_aplicacao)}},
                {
                    "$lookup": {
                        "from": "Respostas",
                        "let": {"aplicacao": "$_id", "usuario": "$participantes"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$id_aplicacao", "$$aplicacao"]},
                                            {"$in": ["$id_usuario", "$$usuario"]},
                                        ]
                                    }
                                },
                            },
                            {"$project": {"notas": 0}},
                        ],
                        "as": "respostas",
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "descricao": 1,
                        "participantes": 1,
                        "respostas": {"_id": 1, "id_usuario": 1, "nota": 1},
                    }
                },
            ]
        )
    ).next()

    usuarios = list(
        db("Boopt", "Usuários").find(
            {"_id": {"$in": r["participantes"]}},
            {
                "_id": {"$toString": "$_id"},
                "nome": {"$concat": ["$nome", " ", "$sobrenome"]},
            },
        )
    )

    respostas = (
        pl.DataFrame(map(str, r["participantes"]))
        .rename({"column_0": "id_usuario"})
        .join(
            pl.DataFrame(r["respostas"]).with_columns(
                pl.col("id_usuario").map_elements(str)
            ),
            on="id_usuario",
            how="left",
        )
        .join(pl.DataFrame(usuarios), left_on="id_usuario", right_on="_id", how="left")
    ).sort("nome", "nota")

    return respostas
