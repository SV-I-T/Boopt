import dash_mantine_components as dmc
import polars as pl
from bson import ObjectId
from dash import html, register_page
from utils.banco_dados import db
from utils.modelo_assessment import VelaAssessment
from utils.modelo_usuario import Role, Usuario, checar_perfil

register_page(
    __name__,
    path="/app/admin/vela/view",
    title="Visualizar Vela Assessment",
)


@checar_perfil(permitir=[Role.DEV, Role.CONS, Role.ADM])
def layout(id: str = None):
    usr = Usuario.atual()

    assessment = VelaAssessment(
        **db("Vela", "Aplicações").find_one(
            {"_id": ObjectId(id), "empresa": usr.empresa}
        )
    )

    if not assessment:
        return [
            dmc.Title("Assessment inexistente", className="titulo-pagina"),
        ]

    respostas_aplicacao: pl.DataFrame = baixar_respostas_aplicacao(id)

    return [
        dmc.Title("Visualizar Vela Assessment", className="titulo-pagina"),
        dmc.Title(
            f'{assessment.descricao} ({assessment.id_.generation_time.strftime("%d/%m/%Y")})',
            className="secao-pagina",
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
                                    ObjectId(row["_id"]).generation_time.strftime(
                                        "%d/%m/%Y %H:%M"
                                    )
                                    if row["_id"]
                                    else "--"
                                ),
                                html.Td(
                                    dmc.Anchor(
                                        children=f'{row["nota"]:.1f}/70',
                                        href=f'/app/vela/resultado/?usr={usr.id}&resposta={row["_id"]}',
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
        db("Vela", "Aplicações").aggregate(
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
                            {
                                "$project": {
                                    "_id": {"$toString": "$_id"},
                                    "id_usuario": {"$toString": "$id_usuario"},
                                    "nota": 1,
                                }
                            },
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

    usuarios = db("Boopt", "Usuários").find(
        {"_id": {"$in": r["participantes"]}},
        {
            "_id": {"$toString": "$_id"},
            "nome": "$nome",
        },
    )

    respostas = (
        pl.DataFrame(map(str, r["participantes"]))
        .rename({"column_0": "id_usuario"})
        .join(
            pl.DataFrame(
                r["respostas"],
                schema={"_id": str, "id_usuario": str, "nota": float},
            ),
            on="id_usuario",
            how="left",
        )
        .join(pl.DataFrame(usuarios), left_on="id_usuario", right_on="_id", how="left")
    ).sort("nome", "nota")

    return respostas
