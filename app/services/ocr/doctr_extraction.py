from app.services.ocr.base_ocr import BaseOCR
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from doctr.models import ocr_predictor


class DoctrOCR(BaseOCR):
    def extrair_texto(self, imagem_path: str) -> str:
        model = ocr_predictor(pretrained=True)
        doc = DocumentFile.from_images(imagem_path)
        result = model(doc)

        texto = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    texto += " ".join([word.value for word in line.words]) + "\n"
        return texto