import ollama
import re
import json 

class LLMStruct:
    def __init__(self):
        self.prompt = """Você retorna APENAS um JSON com as chaves VALOR_TOTAL, DATA, CNPJ e EMPRESA."Retorne APENAS um JSON válido, sem texto extra, sem markdown, sem ```. Você ao receber as informações em texto corrido, estruture em um texto. Exemplo:
{ "VALOR_TOTAL": 1500.83, EMPRESA: RIO DO PEIXE, CNPJ: 25.184.394/0001-20, DATA: 16:02:2026 }"""

    def process(self, dados: str):
        resp = ollama.chat(
            model="gemma3:1B",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": dados}
            ]
        )
        content = resp["message"]["content"]

        content = re.sub(r"```json|```", "", content).strip()

        return json.loads(content)
