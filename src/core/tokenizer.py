
import tiktoken

class Tokenizer:
    def __init__(self, model_name: str = "gpt-4o"):
        """
        Initialize tokenizer for a specific model.
        Defaults to gpt-4o which uses cl100k_base encoding.
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        if not text:
            return 0
        return len(self.encoding.encode(text))
