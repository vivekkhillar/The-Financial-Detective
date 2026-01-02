import logging
import json
import re

logger = logging.getLogger("FinancialDetective")

def setup_logger(name="FinancialDetective"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def clean_json_string(json_str):
    """
    Cleans markdown formatting and extracts JSON from LLM responses.
    Handles multiple formats: markdown code blocks, text with JSON, etc.
    """
    if not json_str:
        return '{"entities": [], "relationships": []}'
    
    # First, try to extract from markdown code blocks
    if "```" in json_str:
        # Try to match ```json ... ``` or ``` ... ```
        patterns = [
            r"```json\s*(.*?)```",  # ```json ... ```
            r"```\s*(.*?)```",      # ``` ... ```
        ]
        for pattern in patterns:
            match = re.search(pattern, json_str, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                # Try to parse it to validate
                try:
                    json.loads(extracted)
                    return extracted
                except:
                    json_str = extracted
                    break
    
    # Try to find JSON object by looking for balanced braces
    # Start from the first { and find the matching }
    start_idx = json_str.find('{')
    if start_idx != -1:
        brace_count = 0
        end_idx = start_idx
        for i in range(start_idx, len(json_str)):
            if json_str[i] == '{':
                brace_count += 1
            elif json_str[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if brace_count == 0:
            json_candidate = json_str[start_idx:end_idx].strip()
            # Try to parse it
            try:
                json.loads(json_candidate)
                return json_candidate
            except:
                pass
    
    # Fallback: try regex pattern matching
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = list(re.finditer(json_pattern, json_str, re.DOTALL))
    
    # Find the largest valid JSON object
    largest_match = None
    largest_size = 0
    for match in matches:
        candidate = match.group(0).strip()
        try:
            json.loads(candidate)  # Validate it's valid JSON
            if len(candidate) > largest_size:
                largest_size = len(candidate)
                largest_match = candidate
        except:
            continue
    
    if largest_match:
        return largest_match
    
    # If no JSON found, return empty JSON object
    logger.warning(f"No valid JSON found in LLM response. First 200 chars: {json_str[:200]}")
    return '{"entities": [], "relationships": []}'