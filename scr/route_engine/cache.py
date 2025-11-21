import json
import hashlib
import os
from typing import Optional, Any
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

def make_cache_key(preferences: dict) -> str:
    s = json.dumps(preferences, sort_keys=True, ensure_ascii=False)
    return "route:" + hashlib.sha256(s.encode('utf-8')).hexdigest()

def get_cached(key: str) -> Optional[dict]:
    v = r.get(key)
    if not v:
        return None
    try:
        return json.loads(v)
    except Exception:
        return None

def set_cached(key: str, value: Any, ttl_seconds: int = 60*60*24):
    r.set(key, json.dumps(value, ensure_ascii=False), ex=ttl_seconds)
