import ollama
from app.services.prompt import PROMPT
from app.services.examples import EXAMPLES
from app.services.ocr.doctr_extraction import DoctrOCR
from app.services.llms.llm_struct import LLMStruct
from app.services.llms.llm_extraction import LLMExtraction
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
            response = ollama.chat(
                model="gemma3:1B",  
                messages=messages
            )
            json_str = response["message"]["content"]
            return json.dumps(json_str)
    
    def extract(image_bytes: bytes):
        doctr: BaseOCR = DoctrOCR()
        llm_extraction = LLMExtraction()
        llm_struct = LLMStruct()
        texto = doctr.extrair_texto(image_bytes)
        extraction = llm_extraction.process(texto)
        result = llm_struct.process(extraction)
        return result






