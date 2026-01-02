"""
Module Description
==================

This module handel all the config details 

:Author: Vivek Khillar
:Date: 2025-12-24
:Version: 1.0
"""

import os
import sys

class Config:

    # Data source - can be URL or local file path
    PDF_URL = "https://www.reliance.com/content/dam/reliance/pdf/annual-reports/2024-25/AR2024-25.pdf"
    
    # Local messy text file (extracted from PDF)
    MESSY_TEXT_FILE = "data/messy_text.txt"
    
    # Use local file instead of URL (set to True to use messy_text.txt)
    USE_LOCAL_FILE = True
    
    # SSL Verification (set to False if SSL certificate issues occur)
    SSL_VERIFY = True

    # LLM API URL 
    LLM_API_URL = "http://10.173.119.32:443/v1"
    LLM_MODEL_NAME = "gemma3:12b"
    MAX_TOKENS = 4000
    temperature = 0.1

    # Output Paths
    OUTPUT_DIR = "output"
    JSON_FILENAME = "graph_output.json"
    GRAPH_FILENAME = "knowledge_graph.png"

    # Extraction Settings
    # To simulate the "messy 5-page excerpt", we process a specific range.
    # Set to None to process the whole file (warning: costly).

    PAGE_LIMIT = slice(0, 5)

    @classmethod
    def get_output_path(cls, filename):
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)
        return os.path.join(cls.OUTPUT_DIR, filename)
    