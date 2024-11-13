from bson import ObjectId

from utils.banco_dados import db
from utils.login import checar_perfil
from utils.missao import Missao
from utils.role import Role
from utils.url import UrlUtils
from utils.usuario import Usuario
from utils.vela import Vela


def carregar_usuarios_empresa(empresa: str):
    usuarios = list(
        db("Usuários").find(
            {"empresa": ObjectId(empresa)},
            {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "usuario": "$nome",
                "cargo": 1,
            },
        )
    )

    return usuarios
