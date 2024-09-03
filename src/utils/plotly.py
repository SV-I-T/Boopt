import plotly.graph_objects as go
import plotly.io as pio

pio.templates["boopt"] = go.layout.Template(
    layout=go.Layout(
        separators=",.",
        font=go.layout.Font(family='"Open Sans",sans-serif,"Segoe UI"', weight=500),
        barcornerradius=10,
        dragmode=False,
        legend=go.layout.Legend(itemclick="toggleothers", itemdoubleclick="toggle"),
    )
)
pio.templates.default = "boopt"


def get_plotly_configs(filename: str = "gráfico_exportado", **kwargs) -> dict:
    configs = {
        "locale": "pt-br",
        "displaylogo": False,
        "toImageButtonOptions": {
            "filename": filename,
            "scale": 2,
            "height": 400,
            "width": 600,
        },
    }
    for k, v in kwargs.items():
        configs[k] = v
    return configs
