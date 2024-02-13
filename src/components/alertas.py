import dash_mantine_components as dmc


def criar_alerta(mensagem: str, cor: str, titulo: str = None) -> dmc.Alert:
    return dmc.Alert(color=cor, children=str(mensagem), title=titulo, my="1rem")
