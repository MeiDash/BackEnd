from pdf2image import convert_from_path

def pdf_to_images(path):
    pages = convert_from_path(path, dpi=200)
    img_paths = []

    for i, page in enumerate(pages):
        img_path = f"page_{i}.png"
        page.save(img_path, "PNG")
        img_paths.append(img_path)

    return img_paths