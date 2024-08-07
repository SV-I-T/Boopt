import re
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, ValidationInfo, computed_field, field_validator
from utils.banco_dados import db
from utils.role import Role
from werkzeug.security import generate_password_hash


class NovoUsuario(BaseModel):
    nome: str
    cpf: str
    email: Optional[str] = None
    data: datetime
    cargo: str
    empresa: ObjectId
    role: Role
    clientes: Optional[list[ObjectId]] = None
    unidades: Optional[list[int]] = None

    class Config:
        arbitrary_types_allowed = True
        str_strip_whitespace = True

    @field_validator("nome", "cpf", "data", "empresa", "cargo", mode="before")
    @classmethod
    def em_branco(cls, v: Any, info: ValidationInfo) -> Any:
        assert bool(v), f"O campo '{info.field_name.capitalize()}' é obrigatório."
        return v

    @field_validator("email")
    @classmethod
    def email_valido(cls, email: str) -> str | None:
        if not email:
            return None
        assert re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        ).fullmatch(email), f"O e-mail {email!r} é inválido."
        return email

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, cpf: str) -> str:
        cpf = cpf.replace(".", "").replace("-", "")
        assert len(cpf) == 11 and cpf.isdigit(), f"O CPF {cpf} é inválido."
        cpf_d = tuple(map(int, cpf))
        resto1 = sum(((10 - i) * n for i, n in enumerate(cpf_d[:9]))) % 11
        regra1 = (resto1 <= 1 and cpf_d[-2] == 0) or (
            resto1 >= 2 and cpf_d[-2] == 11 - resto1
        )
        resto2 = sum(((11 - i) * n for i, n in enumerate(cpf_d[:10]))) % 11
        regra2 = (resto2 <= 1 and cpf_d[-1] == 0) or (
            resto2 >= 2 and cpf_d[-1] == 11 - resto2
        )
        assert regra1 and regra2, f"O CPF {cpf} é inválido."
        assert not db("Usuários").count_documents(
            {"cpf": cpf}
        ), f"O CPF {cpf!r} já foi cadastrado."
        return cpf

    @field_validator("unidades", mode="before")
    @classmethod
    def validar_unidades_codigo(cls, unidades: list):
        try:
            unidades = [int(unidade) for unidade in unidades]
        except ValueError:
            raise AssertionError(
                "As unidades precisam ser representadas pelo seu código cadastrado. Verifique se não foi informado um texto ao invés de um número."
            )
        return unidades

    @computed_field
    @property
    def senha_hash(self) -> str:
        return generate_password_hash(self.data.strftime("%d%m%Y"))

    def registrar(self) -> None:
        r = db("Usuários").insert_one(self.model_dump(exclude_none=True))
        assert (
            r.acknowledged
        ), "Não conseguimos criar o usuário. Tente novamente mais tarde."
