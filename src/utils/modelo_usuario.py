import re
from typing import Any, Literal, Optional

import dash_mantine_components as dmc
from bson import ObjectId
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from pydantic import BaseModel, computed_field, field_validator
from utils.banco_dados import mongo
from werkzeug.security import check_password_hash, generate_password_hash


class NovoUsuario(BaseModel):
    nome: str
    sobrenome: str
    cpf: str
    email: Optional[str] = None
    data: str
    cargo: str
    empresa: str
    admin: bool = False
    gestor: bool = False
    recruta: bool = False

    @field_validator("nome", "sobrenome", "cpf", "data", "cargo", mode="before")
    @classmethod
    def em_branco(cls, v: Any, field) -> Any:
        assert bool(v), "Todos os campos marcados com (*) são obrigatórios"
        return v

    @field_validator("email")
    @classmethod
    def email_valido(cls, email: str) -> str | None:
        if email == "":
            return None
        assert re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        ).fullmatch(email), "Email inválido"
        return email

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, cpf: str) -> str:
        assert len(cpf) == 11 and cpf.isdigit(), "CPF inválido"
        cpf_d = tuple(map(int, cpf))
        resto1 = sum(((10 - i) * n for i, n in enumerate(cpf_d[:9]))) % 11
        regra1 = (resto1 <= 1 and cpf_d[-2] == 0) or (
            resto1 >= 2 and cpf_d[-2] == 11 - resto1
        )
        resto2 = sum(((11 - i) * n for i, n in enumerate(cpf_d[:10]))) % 11
        regra2 = (resto2 <= 1 and cpf_d[-1] == 0) or (
            resto2 >= 2 and cpf_d[-1] == 11 - resto2
        )
        assert regra1 and regra2, "CPF inválido"
        return cpf

    @computed_field
    @property
    def senha_hash(self) -> str:
        return generate_password_hash("".join(self.data.split("-")[::-1]))

    def registrar(self) -> None:
        assert not mongo.cx["Boopt"]["Usuários"].find_one(
            {"cpf": self.cpf}
        ), "Este CPF já está cadastrado"

        r = mongo.cx["Boopt"]["Usuários"].insert_one(self.model_dump())
        assert (
            r.inserted_id
        ), "Não conseguimos criar o usuário. Tente novamente mais tarde."
        # print("Registrando usuário...")


class Usuario(UserMixin, BaseModel):
    _id: Optional[ObjectId] = None
    nome: str
    sobrenome: str
    cpf: str
    email: Optional[str] = None
    cargo: str
    empresa: str
    admin: bool = False
    gestor: bool = False

    @computed_field
    @property
    def id(self) -> str:
        return str(self._id)

    @classmethod
    def entrar(
        cls, identificador: Literal["_id", "email", "cpf"], valor: str, senha: str
    ):
        if identificador == "_id":
            valor = ObjectId(valor)
        usuario = mongo.cx["Boopt"]["Usuários"].find_one({identificador: valor})
        assert usuario, "Usuário não existe"
        assert check_password_hash(usuario["senha_hash"], senha), "Senha incorreta"

        return Usuario(**usuario)

    def sair(self) -> None:
        assert current_user.is_authenticated, "Não logado no momento"
        logout_user()


login_manager = LoginManager()
login_manager.login_view = "/login"


@login_manager.user_loader
def carregar_usuario(_id):
    return Usuario.carregar(identificador="_id", valor=_id)


def layout_nao_autorizado():
    return dmc.Container(children=dmc.Text(children="Não autorizado"))


def checar_login(func: callable):
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return layout_nao_autorizado()

    return wrapper
