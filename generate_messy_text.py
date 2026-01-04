""" Script to extract text from PDF and create a messy text file """
import sys
import re
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
            # Extract text from page
            try:
                text = page.extract_text()
            except Exception as e:
                logger.warning(f"Error extracting text from page {i+1}: {e}")
                text = None
            
            if text:
                # Normalize text encoding to preserve special characters
                # This helps preserve the original intent before further processing
                try:
                    text = text.encode('utf-8', errors='replace').decode('utf-8')
                except Exception as e:
                    logger.warning(f"Error encoding text from page {i+1}: {e}")
                    # Continue with text as-is if encoding fails
                
                # Make it messy - add some formatting issues
                messy_text = f"--- PAGE {i+1} ---\n{text}\n\n"
                text_content.append(messy_text)
        
        full_text = "\n".join(text_content)
        
        # Fix currency symbol corruption from PDF extraction
        # CRITICAL: Both $ and ₹ are corrupted to "L" during PDF extraction
        # We need to distinguish based on context (Indian vs US context)
        logger.info("Fixing currency symbol corruption (both $ and ₹ corrupted to 'L')...")
        
        # STEP 1: Fix rupee symbol issues FIRST (Indian context takes priority)
        # Pattern: "j" or "J" before numbers likely means "₹" (if not already corrupted to L)
        full_text = re.sub(r'\b([jJ])\s*(\d)', r'₹\2', full_text)
        # Fix "Rs." that got corrupted to "Rj" or "RL" or similar
        full_text = re.sub(r'\bR[jJ]\s*\.?\s*(\d)', r'₹\1', full_text)
        full_text = re.sub(r'\bR[Ll]\s*\.?\s*(\d)', r'₹\1', full_text)
        # Fix "INR" or "Rs" that might be corrupted
        full_text = re.sub(r'\bIN[Rr]\s*(\d)', r'₹\1', full_text)
        full_text = re.sub(r'\bR[sS]\s*\.?\s*(\d)', r'₹\1', full_text)
        
        # STEP 2: Fix "L" that represents rupee (₹) - Indian context indicators
        # Priority: Fix rupee symbols FIRST based on Indian context
        # Indian numbering pattern: L1,23,456 or L1,23,456.78 (comma-separated in Indian format)
        # Pattern 1: L followed by Indian numbering (1,23,456 format) with crore/lakh
        full_text = re.sub(r'\bL\s*(\d{1,2}(?:,\d{2})*(?:,\d{3})*(?:\.\d+)?)\s*(crore|lakh|thousand)', r'₹\1 \2', full_text, flags=re.IGNORECASE)
        # Pattern 2: L with Indian comma pattern (e.g., L1,23,456 or L12,34,567) - at least 2 comma groups
        full_text = re.sub(r'\bL\s*(\d{1,2}(?:,\d{2}){2,}(?:,\d{3})*(?:\.\d+)?)', r'₹\1', full_text)
        # Pattern 3: L followed by numbers in lines containing Indian financial terms (conservative approach)
        # Split into sentences/lines and check context
        lines = full_text.split('\n')
        fixed_lines = []
        for line in lines:
            # If line contains Indian financial terms and "L" before numbers, likely rupee
            if re.search(r'\b(revenue|profit|asset|debt|equity|turnover|sales|income|expense|investment|capital|fund|contribution|csr|reliance|india|indian)\b', line, re.IGNORECASE):
                # Fix L before numbers in this line
                line = re.sub(r'\bL\s*(\d{1,2}(?:,\d{2})*(?:,\d{3})*(?:\.\d+)?)', r'₹\1', line)
            fixed_lines.append(line)
        full_text = '\n'.join(fixed_lines)
        
        # STEP 3: Fix "L" that represents dollar ($) - US/international context
        # Only fix remaining "L" that are clearly in US/international context
        # Pattern: "US" followed by "L" means dollar
        full_text = re.sub(r'\bUS\s*([Ll])\s*(\d)', r'US$ \2', full_text)
        # Pattern: "L" followed by numbers with "billion" or "million" (US context)
        full_text = re.sub(r'\b([Ll])\s*(\d+\.?\d*)\s*(billion|million)\b', r'$\2 \3', full_text, flags=re.IGNORECASE)
        # Pattern: "L" with US-style comma pattern (e.g., L1,234,567) - but only if not already fixed as rupee
        # This is tricky - we need to be careful not to override rupee fixes
        # Only apply if it's clearly US context (no Indian financial terms nearby)
        
        # STEP 4: Fix any remaining standalone "L" before numbers that weren't caught
        # This should be minimal after the above fixes
        # Only fix if it's clearly a currency symbol (not "L" meaning "Lakh" in text)
        # Look for patterns like "L 123" or "L123" where L is likely a currency symbol
        # But be conservative - only fix if it's in a financial context
        full_text = re.sub(r'\b([Ll])\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(billion|million)\b', r'$\2 \3', full_text, flags=re.IGNORECASE)
        
        logger.info("Currency symbol fixes applied (rupee priority, then dollar)")
        
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
    extract_messy_text(pdf_path, output_path, pages=5)
    print(f"\nMessy text file created: {output_path}")

