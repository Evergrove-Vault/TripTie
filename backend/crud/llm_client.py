"""
Клиент для работы с LLM (Ollama)
"""
import os
import requests
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Настройки Ollama
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

def call_llm(system_prompt: str, user_prompt: str, model: str = None) -> Tuple[bool, str]:
    """
    Вызывает LLM через Ollama API.
    Возвращает (ok, content). ok=False если ошибка.
    """
    if model is None:
        model = OLLAMA_MODEL
    
    # Формируем промпт для Ollama
    full_prompt = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000,
                    "stop": ["<|im_end|>"]
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "").strip()
            return True, content
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return False, f"Ошибка API: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {e}")
        return False, f"Сетевая ошибка: {e}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False, f"Неожиданная ошибка: {e}"

def check_ollama_available() -> bool:
    """Проверяет, доступен ли Ollama сервер"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

