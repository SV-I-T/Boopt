import re
from typing import Any, Literal, Optional

import dash_mantine_components as dmc
from bson import ObjectId
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from pydantic import BaseModel, Field, computed_field, field_validator
from utils.banco_dados import db
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

    class Config:
        str_strip_whitespace = True

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
        assert not db("Boopt", "Usuários").find_one(
            {"cpf": self.cpf}
        ), "Este CPF já está cadastrado"

        r = db("Boopt", "Usuários").insert_one(self.model_dump())
        assert (
            r.acknowledged
        ), "Não conseguimos criar o usuário. Tente novamente mais tarde."


class Usuario(BaseModel, UserMixin):
    id_: ObjectId = Field(alias="_id")
    nome: str
    sobrenome: str
    data: str
    senha_hash: str
    cpf: str
    email: str
    cargo: str
    empresa: str
    recruta: bool = False
    admin: bool = False
    gestor: bool = False

    class Config:
        arbitrary_types_allowed = True

    @computed_field
    @property
    def id(self) -> str:
        return str(self.id_)

    @classmethod
    def buscar(cls, identificador: Literal["_id", "email", "cpf"], valor: str):
        if identificador == "_id":
            valor = ObjectId(valor)
        usr = db("Boopt", "Usuários").find_one({identificador: valor})
        assert usr, "Usuário não existe."

        return cls(**usr)

    def validar_senha(self, senha: str) -> None:
        assert check_password_hash(self.senha_hash, senha), "Senha incorreta."

    def alterar_senha(
        self, senha_atual: str, senha_nova: str, senha_nova_check: str
    ) -> bool:
        senha_hash = db("Boopt", "Usuários").find_one(
            {"_id": self.id_}, {"_id": 0, "senha_hash": 1}
        )["senha_hash"]
        assert check_password_hash(
            senha_hash, senha_atual
        ), "A senha atual não está correta."

        assert not check_password_hash(
            senha_hash, senha_nova
        ), "A senha nova não pode ser igual à senha atual."

        assert (
            senha_nova == senha_nova_check
        ), "As senhas novas inseridas não são iguais."

        r = db("Boopt", "Usuários").update_one(
            {"_id": self.id_},
            {"$set": {"senha_hash": generate_password_hash(senha_nova)}},
        )
        assert r.acknowledged, "Ocorreu algum problema, tente novamente mais tarde."
        return True


login_manager = LoginManager()
login_manager.login_view = "/login"


@login_manager.user_loader
def carregar_usuario(_id):
    if _id == "None":
        return None
    usr = db("Boopt", "Usuários").find_one(
        {"_id": ObjectId(_id)},
    )
    if not usr:
        return None
    return Usuario(**usr)


def layout_nao_autorizado():
    return [
        dmc.Title(children="Ops!", order=1),
        dmc.Title(
            children="Parece que você não tem autorização para acessar essa página",
            order=3,
            weight=500,
        ),
        dmc.Anchor(
            children="Clique aqui para voltar à página inicial",
            href="/",
            underline=True,
        ),
    ]


def checar_login(_func=None, *, admin: bool = False, gestao: bool = False):
    def decorador(func: callable):
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                if admin and current_user.admin or not admin:
                    return func(*args, **kwargs)
            return layout_nao_autorizado()

        return wrapper

    if _func is None:
        return decorador
    else:
        return decorador(_func)
