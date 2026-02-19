from pdf2image import convert_from_path
from datetime import datetime

def pdf_to_images(path):
    pages = convert_from_path(path, dpi=200)
    img_paths = []

    for i, page in enumerate(pages):
        img_path = f"page_{i}.png"
        page.save(img_path, "PNG")
        img_paths.append(img_path)

    return img_paths

def format_value(valor: float) -> str:
    """Formata float para moeda brasileira: R$ 1.234,56"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date(data) -> str:
    """Formata date/datetime para dd/mm/aaaa."""
    if data is None or data=="":
        return "-"
    if isinstance(data, datetime):
        return data.strftime("%d/%m/%Y")
    return data.strftime("%d/%m/%Y")