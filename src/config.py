import os
import sys

class Config:

    # Local messy text file (extracted from PDF)
    MESSY_TEXT_FILE = "data/messy_text.txt"
    
    # LLM API URL 
    LLM_API_URL = "http://10.173.119.32:443/v1"
    LLM_MODEL_NAME = "gemma3:12b"
    MAX_TOKENS = 6000
    temperature = 0.1

    # Output Paths
    OUTPUT_DIR = "output"
    JSON_FILENAME = "graph_output.json"
    GRAPH_FILENAME = "knowledge_graph.png"
    
    # Tokenization Settings
    TOKENIZE_TEXT = True  # Enable text tokenization/cleaning
    CLEAN_TEXT = True  # Enable text cleaning (set to False to preserve original text structure)
    CHUNK_TEXT = True  # Enable text chunking (set to True for very long texts)
    CHUNK_SIZE = 4000  # Maximum characters per chunk
    CHUNK_OVERLAP = 300  # Characters to overlap between chunks
    CHUNK_STRATEGY = "fixed"  # Options: "sentence", "paragraph", "fixed"

    @classmethod
    def get_output_path(cls, filename):
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)
        return os.path.join(cls.OUTPUT_DIR, filename)
    