from enum import Enum


class Role(str, Enum):
    DEV = "Desenvolvedor"
    CONS = "Consultor"
    ADM = "Administrador"
    GEST = "Gestor"
    USR = "Usuário"
    CAND = "Candidato"

    def consultar_roles_acessiveis(self):
        if self == Role.DEV:
            return [r for r in Role]
        elif self == Role.CONS:
            return [Role.ADM, Role.GEST, Role.USR]
        elif self == Role.ADM:
            return [Role.GEST, Role.USR]
