from datetime import datetime
from typing import Any, Literal, Optional

from bson import ObjectId
from flask_login import UserMixin, current_user
from pydantic import BaseModel, Field, computed_field
from pymongo.cursor import Cursor
from utils.banco_dados import db
from utils.cache import cache_simple
from utils.role import Role
from werkzeug.security import check_password_hash

CARGOS_PADROES = sorted(
    [
        "Vendedor",
        "Diretor Comercial",
        "Gerente de Loja",
        "Atendente",
        "Supervisor de Loja",
        "Regional",
    ]
)


class Usuario(BaseModel, UserMixin):
    id_: ObjectId = Field(alias="_id")
    nome: Optional[str] = None
    data: Optional[datetime] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    role: Optional[Role] = Role.CAND
    empresa: Optional[ObjectId] = None
    clientes: Optional[list[ObjectId]] = Field(default_factory=list)
    cargo: Optional[str] = None
    unidades: Optional[list[int]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    @classmethod
    def atual(cls):
        atual: Usuario = current_user
        return atual

    @computed_field
    @property
    def id(self) -> str:
        return str(self.id_)

    @computed_field
    @property
    def primeiro_nome(self) -> str:
        return self.nome.split(" ")[0]

    @classmethod
    def buscar(
        cls, identificador: Literal["_id", "email", "cpf"], valor: str | ObjectId
    ):
        if identificador == "_id" and not isinstance(valor, ObjectId):
            valor = ObjectId(valor)
        usr = db("Usuários").find_one({identificador: valor})
        assert usr, "Este usuário não foi encontrado."

        return cls(**usr)

    @classmethod
    @cache_simple.memoize(timeout=600)
    def buscar_login(cls, _id: str) -> dict | None:
        if _id == "None":
            return None
        usr = db("Usuários").find_one(
            {"_id": ObjectId(_id)},
        )
        print(f"Carregando usuário {usr['nome']}")
        return usr

    def validar_senha(self, senha: str) -> None:
        assert check_password_hash(
            self.senha_hash, senha
        ), "A senha digitada está incorreta."

    def atualizar(self, novos_dados: dict[str, Any]) -> None:
        r = db("Usuários").update_one(
            {"_id": self.id_},
            {
                "$set": {campo: valor for campo, valor in novos_dados.items() if valor},
                "$unset": {
                    campo: 1 for campo, valor in novos_dados.items() if not valor
                },
            },
        )

        assert r.acknowledged, "Ocorreu algum problema. Tente novamente mais tarde."

    def buscar_empresas(
        self, project_fields: list[str] = ["_id", "nome"]
    ) -> Cursor | list:
        if self.role == Role.DEV:
            query = {}
        elif self.role == Role.CONS:
            query = {"_id": {"$in": self.clientes}}
        elif self.role == Role.ADM:
            query = {"_id": self.empresa}
        elif self.role == Role.GEST:
            query = {"_id": self.empresa, "unidade": {"$in": self.unidades}}

        else:
            return []

        return db("Empresas").find(
            query, projection={field: 1 for field in project_fields}, sort={"nome": 1}
        )
