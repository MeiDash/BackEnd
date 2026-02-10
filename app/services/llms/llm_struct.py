import ollama
from ollama import Client
import re
import json 

URL_REMOTA = "https://hiking-indiana-yard-luggage.trycloudflare.com"
client = Client(host=URL_REMOTA)

class LLMStruct:
    def __init__(self):
        self.prompt = """Você retorna APENAS um JSON com as chaves VALOR_TOTAL, DATA, CNPJ e EMPRESA."Retorne APENAS um JSON válido, sem texto extra, sem markdown, sem ```. Você ao receber as informações em texto corrido, estruture em um json. Exemplo:
{ "VALOR_TOTAL": 1500.83, EMPRESA: RIO DO PEIXE, CNPJ: 25.184.394/0001-20, DATA: 16:02:2026 }"""

    def process(self, dados: str):
        resp = client.chat(
            model="gemma3:1B",
            format="json",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": dados}
            ]
        )
        content = resp["message"]["content"]

        content = re.sub(r"```json|```", "", content).strip()

        return json.loads(content)
