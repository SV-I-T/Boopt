import re

query_params = re.compile("([^=&?]+)=([^=&?]+)")


class QParams:
    @classmethod
    def extrair_params(cls, query_string: str) -> dict[str, str]:
        return dict(query_params.findall(query_string))

    @classmethod
    def construir_query_string(cls, params: dict[str, str]) -> str:
        return "?" + "&".join([f"{k}={v}" for k, v in params.values()])
