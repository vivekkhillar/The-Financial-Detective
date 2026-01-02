"""
Script to extract text from PDF and create a messy text file
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pypdf import PdfReader
from src.config import Config
from src.utils import setup_logger

logger = setup_logger()

def extract_messy_text(pdf_path, output_path, pages=5):
    """
    Extract text from first N pages of PDF and create a messy text file
    """
    try:
        logger.info(f"Reading PDF from {pdf_path}...")
        reader = PdfReader(pdf_path)
        
        # Extract first N pages (messy excerpt)
        text_content = []
        total_pages = min(pages, len(reader.pages))
        
        logger.info(f"Extracting text from first {total_pages} pages...")
        
        for i in range(total_pages):
            page = reader.pages[i]
            text = page.extract_text()
            if text:
                # Make it messy - add some formatting issues
                messy_text = f"--- PAGE {i+1} ---\n{text}\n\n"
                text_content.append(messy_text)
        
        full_text = "\n".join(text_content)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        logger.info(f"Created messy text file: {output_path}")
        logger.info(f"Total characters: {len(full_text)}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        raise

if __name__ == "__main__":
    # Path to PDF
    pdf_path = Path("PDF/RIL-Integrated-Annual-Report-2024-25.pdf")
    
    # Output text file path
    output_path = Path("data/messy_text.txt")
    
    # Create data directory if it doesn't exist
    output_path.parent.mkdir(exist_ok=True)
    
    # Extract messy text (first 5 pages)
    extract_messy_text(pdf_path, output_path, pages=160)
    print(f"\nMessy text file created: {output_path}")

