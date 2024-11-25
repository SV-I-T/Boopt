from typing import Any, Literal

import dash_mantine_components as dmc

NOTIFICATION_STATUS_MAPPING = {
    "success": ("Pronto!", "green"),
    "warning": ("Atenção!", "yellow"),
    "error": ("Ops!", "red"),
}


def nova_notificacao(
    id: str, message: Any, type: str = Literal["success", "warning", "error"]
) -> dmc.Notification:
    title, color = NOTIFICATION_STATUS_MAPPING.get(type)
    return dmc.Notification(
        id=id,
        title=title,
        message=message,
        color=color,
        action="show",
    )
