from ocr import BaseOCR

class EasyOCR(BaseOCR):
    def extrair_texto(self, imagem_path: str) -> str:
        reader = easyocr.Reader(['pt'])
        result = reader.readtext(imagem_path)

        texto = ""
        for (_, txt, conf) in result:
            texto += txt + "\n"
        return texto
