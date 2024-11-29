import openpyxl
from bson import ObjectId
from pydantic import BaseModel, Field

from utils.banco_dados import db
from utils.novo_usuario import NovoUsuario
from utils.role import Role


class MultipleErrors(ValueError): ...


# @cache.memoize(timeout=5)
def buscar_unidades_empresa(id_empresa: ObjectId) -> list[int]:
    unidades: list[int] = (
        db("Empresas")
        .aggregate(
            [
                {"$match": {"_id": id_empresa}},
                {
                    "$set": {
                        "unidades": {
                            "$map": {
                                "input": "$unidades",
                                "as": "unidade",
                                "in": "$$unidade.cod",
                            }
                        }
                    }
                },
                {"$project": {"unidades": 1, "_id": 0}},
            ]
        )
        .next()["unidades"]
    )

    return unidades


def verificar_unidades_cadastradas(usuarios: list[NovoUsuario]) -> None:
    unidades_empresa = buscar_unidades_empresa(usuarios[0].empresa)
    erros = []
    for linha, usuario in enumerate(usuarios, start=1):
        if usuario.unidades is None:
            usuario.unidades = []
            continue
        for unidade in usuario.unidades:
            if unidade not in unidades_empresa:
                erros.append({"loc": linha, "unidade": unidade})

    if erros:
        raise MultipleErrors(erros)


class NovosUsuariosBatelada(BaseModel):
    usuarios: list[NovoUsuario] = Field(default_factory=list)

    def registrar_usuarios(self) -> None:
        verificar_unidades_cadastradas(self.usuarios)

        # return
        r = db("Usuários").insert_many(
            [usuario.model_dump() for usuario in self.usuarios]
        )
        assert (
            r.acknowledged
        ), "Não conseguimos criar os usuários. Tente novamente mais tarde."

    @classmethod
    def carregar_planilha(cls, planilha, empresa: ObjectId, role: Role):
        wb = openpyxl.load_workbook(planilha)
        assert (
            "Cadastro" in wb.sheetnames
        ), "A planilha 'Cadastro' não foi encontrada. Certifique-se que o arquivo segue o modelo fornecido."
        ws = wb["Cadastro"]
        linhas = [[cell.value for cell in row] for row in ws.rows]
        assert (
            [
                "Nome completo*",
                "CPF*",
                "Data de Nascimento*",
                "Email",
                "Cargo/Função*",
                "Unidade(s)",
            ]
            == linhas[0]
        ), "O arquivo não está no modelo esperado. Certifique-se de não modificar o cabeçalho do modelo fornecido."

        assert (
            len(linhas) > 1
        ), "Parece que o arquivo está vazio. Preencha-o e tente enviar novamente."

        usuarios = [
            {
                "nome": linha[0],
                "cpf": linha[1],
                "data": linha[2],
                "email": linha[3] if linha[3] is not None else "",
                "cargo": linha[4],
                "empresa": empresa,
                "role": role,
                "unidades": str(linha[5]).split(";") if linha[5] is not None else None,
            }
            for linha in linhas[1:]
        ]

        return cls(usuarios=usuarios)
