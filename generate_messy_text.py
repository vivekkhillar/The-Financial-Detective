""" Script to extract text from PDF and create a messy text file """
import sys
from pathlib import Path
from pypdf import PdfReader
from src.config import Config
from src.utils import setup_logger

logger = setup_logger()

def extract_messy_text(pdf_path, output_path, pages=5):
    """ Extract text from PDF and create a messy text file """
    try:

        logger.info(f"Reading PDF from {pdf_path}...")
        reader = PdfReader(pdf_path)
        
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

    # Path to PDF where annual report is stored    
    pdf_path = Path("PDF/RIL-Integrated-Annual-Report-2024-25.pdf")
    
    # Output text file path where messy text will be stored
    output_path = Path("data/messy_text.txt")
    
    # Create data directory if it doesn't exist where messy text will be stored
    output_path.parent.mkdir(exist_ok=True)
    
    # Extract messy text from function extract_messy_text
    extract_messy_text(pdf_path, output_path, pages=160)
    print(f"\nMessy text file created: {output_path}")

