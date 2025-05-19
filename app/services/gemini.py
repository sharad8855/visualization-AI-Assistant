class GeminiService:
    def __init__(self):
        self.api_key = None

    def initialize(self, api_key: str):
        self.api_key = api_key

    def generate_response(self, prompt: str) -> str:
        # Dummy implementation
        return f"Response to: {prompt}" 