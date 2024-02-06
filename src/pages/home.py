import dash_mantine_components as dmc
from dash import dcc, html, register_page

register_page(__name__, path="/", title="Início")


def layout():
    return [
        dmc.Title("Lorem ipsum dolor sit amet consectetur adipiscing elit.", order=1),
        dmc.Text(
            size="xs",
            children="Nam quis risus vitae sapien vulputate rutrum a malesuada sem. Vestibulum at orci sit amet urna bibendum tincidunt. Vestibulum convallis lorem id tellus facilisis, eget fermentum massa blandit. Curabitur condimentum ex ipsum, quis eleifend libero condimentum at. Fusce nec mauris eu felis posuere vehicula. Suspendisse nunc diam, faucibus nec faucibus eget, pretium et lorem. Nulla facilisi. Duis vitae rutrum leo. In at facilisis risus, sed placerat ex. Nulla sed leo in risus rutrum porttitor placerat id lectus. Sed sit amet justo lobortis, dignissim odio sed, iaculis augue. Vivamus eget viverra velit. Nunc in cursus nibh. Nulla odio massa, facilisis ut nunc id, cursus maximus arcu. Curabitur consectetur eu ex non malesuada.",
        ),
    ]
