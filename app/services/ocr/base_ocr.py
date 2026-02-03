from abc import ABC, abstractmethod

class BaseOCR(ABC):
    @abstractmethod
    def extrair_texto(self, imagem_path: str) -> str:
        pass
