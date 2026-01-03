import logging
import json
import os

logger = logging.getLogger("FinancialDetective")

def setup_logger(name="FinancialDetective"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        
        # Import Config here to avoid circular import issues
        from .config import Config
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = Config.OUTPUT_DIR
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file_path = os.path.join(log_dir, Config.LOG_FILENAME)
        file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.setLevel(logging.INFO)
        logger.info(f"Logger initialized. Log file: {log_file_path}")
        
    return logger

def clean_json_string(json_str):
    """
    Cleans markdown formatting and extracts JSON from LLM responses.
    Uses ONLY string operations (NO REGEX) to comply with competition constraints.
    Handles multiple formats: markdown code blocks, text with JSON, etc.
    """
    if not json_str:
        return '{"entities": [], "relationships": []}'
    
    # First, try to extract from markdown code blocks using string operations only
    if "```" in json_str:
        # Try to find ```json ... ``` or ``` ... ```
        json_str_lower = json_str.lower()
        
        # Look for ```json
        json_marker = "```json"
        if json_marker in json_str_lower:
            start_marker = json_str_lower.find(json_marker)
            start_content = start_marker + len(json_marker)
            # Find the closing ```
            end_marker = json_str.find("```", start_content)
            if end_marker != -1:
                extracted = json_str[start_content:end_marker].strip()
                # Try to parse it to validate
                try:
                    json.loads(extracted)
                    return extracted
                except:
                    json_str = extracted
        
        # If no ```json found, try generic ```
        elif "```" in json_str:
            first_backtick = json_str.find("```")
            start_content = first_backtick + 3
            # Find the next closing ```
            end_marker = json_str.find("```", start_content)
            if end_marker != -1:
                extracted = json_str[start_content:end_marker].strip()
                # Try to parse it to validate
                try:
                    json.loads(extracted)
                    return extracted
                except:
                    json_str = extracted
    
    # Try to find JSON object by looking for balanced braces (NO REGEX)
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
    
    # Fallback: Try to find multiple JSON objects by scanning for balanced braces
    # This is a simple approach without regex - find all potential JSON objects
    json_candidates = []
    search_start = 0
    
    while True:
        start_idx = json_str.find('{', search_start)
        if start_idx == -1:
            break
        
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
            candidate = json_str[start_idx:end_idx].strip()
            try:
                json.loads(candidate)  # Validate it's valid JSON
                json_candidates.append((candidate, len(candidate)))
            except:
                pass
        
        search_start = end_idx
    
    # Find the largest valid JSON object
    if json_candidates:
        largest_match = max(json_candidates, key=lambda x: x[1])[0]
        return largest_match
    
    # If no JSON found, return empty JSON object
    logger.warning(f"No valid JSON found in LLM response. First 200 chars: {json_str[:200]}")
    return '{"entities": [], "relationships": []}'