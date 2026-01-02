import requests
import io
from pathlib import Path
from pypdf import PdfReader
from .utils import setup_logger
from .config import Config

logger = setup_logger()

class PDFLoader:
    def __init__(self, url=None):
        self.url = url or Config.PDF_URL

    def load_from_local_file(self, file_path):
        """Load text from local messy text file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Text file not found: {file_path}")
            
            logger.info(f"Reading messy text file from {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Loaded {len(text)} characters from text file.")
            return text
        except Exception as e:
            logger.error(f"Error loading text file: {e}")
            raise

    def fetch_and_parse(self, page_range=None):
        """
        Loads text from local file or downloads PDF and extracts text.
        """
        # Use local file if configured
        if Config.USE_LOCAL_FILE and Path(Config.MESSY_TEXT_FILE).exists():
            return self.load_from_local_file(Config.MESSY_TEXT_FILE)
        
        # Otherwise, download from URL
        try:
            logger.info(f"Fetching PDF from {self.url}...")
            # Use SSL verification setting from config
            response = requests.get(self.url, timeout=30, verify=Config.SSL_VERIFY)
            response.raise_for_status()
            
            f = io.BytesIO(response.content)
            reader = PdfReader(f)
            
            text_content = []
            pages = reader.pages[page_range] if page_range else reader.pages
            
            logger.info(f"Processing {len(pages)} pages...")
            
            for i, page in enumerate(pages):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- PAGE {i+1} ---\n{text}")
            
            full_text = "\n".join(text_content)
            logger.info(f"Extracted {len(full_text)} characters.")
            return full_text

        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise