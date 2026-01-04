from pathlib import Path
from .utils import setup_logger
from .config import Config

logger = setup_logger()

class PDFLoader:
    
    def __init__(self, file_path=None):
        """
        Initialize PDFLoader with local file path.
        """
        self.file_path = file_path or Config.MESSY_TEXT_FILE

    def fetch_messy_text(self, file_path=None):
        
        """
        Load text from local messy text file.
        Always loads from messy_text.txt file.
        """
        file_path = file_path or self.file_path

        try:
            
            file_path = Path(file_path)
            logger.info(f"File path: {file_path}")
            
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