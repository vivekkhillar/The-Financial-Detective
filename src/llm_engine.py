from openai import OpenAI
from src.config import Config
from src.utils import setup_logger

logger = setup_logger()

class LLMEngine:
    def __init__(self):
        # Initialize OpenAI client pointing to the local server
        self.client = OpenAI(
            base_url=Config.LLM_API_URL,
            api_key="sk-placeholder" # Local servers usually ignore this
        )

    def generate_extraction(self, prompt, context_text):
        # Safety limit: truncate if text is still too long (shouldn't happen if chunking works)
        max_context_length = 12000
        if len(context_text) > max_context_length:
            logger.warning(f"Context text still too long ({len(context_text)} chars), truncating to {max_context_length}")
            context_text = context_text[:max_context_length]
        
        messages = [
            {"role": "system", "content": "You are a JSON-only API. You MUST respond with ONLY valid JSON. No explanations, no markdown, no text before or after. Just pure JSON starting with { and ending with }."},
            {"role": "user", "content": f"{prompt}\n\nTEXT TO ANALYZE:\n{context_text}\n\nRemember: Output ONLY valid JSON, nothing else."}
        ]
    
        try:
            logger.info("Sending request to LLM...")
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL_NAME,
                messages=messages,
                temperature=Config.temperature,
                max_tokens=Config.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API Error: {e}")
            raise