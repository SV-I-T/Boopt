from dash import register_page

register_page(
    __name__,
    path="/assessment-vendedor",
    title="Assessment",
    redirect_from=["/dashboard"],
)


def layout():
    return None
