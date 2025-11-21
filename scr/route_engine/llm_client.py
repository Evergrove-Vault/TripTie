import os
import json
from typing import Tuple
import time

import openai  

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("Требуется OPENAI_API_KEY в окружении")

openai.api_key = OPENAI_KEY

def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> Tuple[bool, str]:
    """
    Возвращает (ok, content). ok=False если ошибка.
    Подбирай model под доступ в твоём аккаунте.
    """
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            timeout=30
        )
        content = resp.choices[0].message.get("content", "")
        return True, content
    except Exception as e:
        return False, f"LLM error: {e}"
