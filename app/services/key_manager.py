from typing import Dict, Optional

class KeyManager:
    def __init__(self):
        self.keys: Dict[str, str] = {}

    def add_key(self, service: str, key: str):
        self.keys[service] = key

    def get_key(self, service: str) -> Optional[str]:
        return self.keys.get(service) 