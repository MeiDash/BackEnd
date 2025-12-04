import ollama
from app.services.prompt import PROMPT
from app.services.examples import EXAMPLES
from sqlalchemy.orm import Session
from sqlalchemy import or_
import tempfile
import json
from typing import Optional, List

class ExtractionService:

    @staticmethod
    def extract_total_value(image_bytes: bytes):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            messages = [
                {"role": "system", "content": PROMPT}
            ]
            for example in EXAMPLES:
                messages.append(example)

            messages.append(
                {
                        "role": "user",
                        "content": "Aqui está uma nota fiscal, extraia seu valor total no formato que lhe foi informado",
                        "images": [tmp_path]
                }
            )
            print(messages)
            print(f"chegou aqui {tmp_path}")
            response = ollama.chat(
                model="llama3.2-vision:latest",  
                messages=messages
            )
            print(f"response {response}")
            json_str = response["message"]["content"]
            return json.dumps(json_str)




