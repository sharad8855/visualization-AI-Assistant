from typing import Any, Dict

def format_response(success: bool, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "data": data or {}
    } 