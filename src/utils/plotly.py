import plotly.graph_objects as go
import plotly.io as pio

pio.templates["boopt"] = go.layout.Template(
    layout=go.Layout(
        colorway=["#FF7730", "#FAC82C"],
        separators=",.",
        images=[
            go.layout.Image(
                source="/assets/imgs/vela/tag_ass.svg",
                opacity=0.5,
                xref="paper",
                yref="paper",
                x=1,
                y=1.05,
                sizex=0.2,
                sizey=0.2,
                xanchor="right",
                yanchor="bottom",
            )
        ],
        font=go.layout.Font(
            family='"Plus Jakarta Sans","Open Sans",sans-serif,"Segoe UI"', weight=500
        ),
        barcornerradius=10,
    )
)
pio.templates.default = "boopt"


def get_plotly_configs(filename: str = "gráfico_exportado", **kwargs) -> dict:
    configs = {
        "locale": "pt-br",
        "displaylogo": False,
        "frameMargins": 0,
        "scrollZoom": False,
        "showTips": True,
        "toImageButtonOptions": {"filename": filename},
    }
    for k, v in kwargs.items():
        configs[k] = v
    return configs
