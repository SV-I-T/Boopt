import re

query_params_re = re.compile("([^=&?]+)=([^=&?]+)")


class UrlUtils:
    @classmethod
    def parse_qparams(cls, query: str) -> dict:
        return dict(query_params_re.findall(query))

    @classmethod
    def build_qstring(cls, params: dict) -> str:
        return "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    @classmethod
    def parse_pparams(cls, path: str, key: str) -> str | None:
        r = re.findall(f"/{key}/([^/?&]+)", path)
        if not r:
            return None
        return r[0]
