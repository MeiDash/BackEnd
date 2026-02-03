import ollama

class LLMExtraction:
    def __init__(self):
        self.prompt = "Você é um extrator de informações. Extraia o valor total e o nome da empresa da nota."

    def process(self, texto: str) -> str:
        resp = ollama.chat(
            model="llama3.2-vision:latest",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": texto}
            ]
        )
        return resp["message"]["content"]