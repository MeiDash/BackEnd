import ollama
from ollama import Client

URL_REMOTA = "https://hiking-indiana-yard-luggage.trycloudflare.com"

client = Client(host=URL_REMOTA)

class LLMExtraction:
    def __init__(self):
        self.prompt = "Você é um extrator de informações. Extraia da nota o valor total, nome da empresa fornecedora, a data e o cnpj."

    def process(self, texto: str) -> str:
        resp = client.chat(
            model="llama3.2-vision:latest",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": texto}
            ]
        )
        return resp["message"]["content"]