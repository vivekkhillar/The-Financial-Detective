import json
# Path setup happens automatically when src is imported (see src/__init__.py)
from src.config import Config
from src.data_loader import PDFLoader
from src.tokenizer import TextTokenizer
from src.extractor import FinancialDetective
from src.visualizer import GraphVisualizer
from src.utils import setup_logger

def main():
    
    logger = setup_logger()
    logger.info("Starting The Financial Detective...")

    # 1. Fetch Data (from local messy_text.txt file)
    loader = PDFLoader()
    raw_text = loader.fetch_messy_text()
    logger.info(f"Raw text loaded: {len(raw_text)} characters")

    # 2. Tokenize and clean text (NO REGEX used)
    if Config.TOKENIZE_TEXT:
        logger.info("Tokenizing and cleaning text using string operations only...")
        
        tokenizer = TextTokenizer(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        tokenized_data = tokenizer.tokenize(
            raw_text,
            clean=Config.CLEAN_TEXT,  # Use config setting for cleaning
            chunk=Config.CHUNK_TEXT,
            chunk_strategy=Config.CHUNK_STRATEGY
        )
        processed_text = tokenized_data['text']
        logger.info(f"Text processed: {tokenized_data['original_length']} -> {tokenized_data['processed_length']} characters")
        if Config.CHUNK_TEXT and 'chunks' in tokenized_data:
            logger.info(f"Text chunked into {tokenized_data['chunk_count']} chunks")
    else:
        processed_text = raw_text
        logger.info("Tokenization skipped, using raw text")

    # 3. Extract Info via LLM
    detective = FinancialDetective()
    graph_data = detective.analyze(processed_text)
    
    # Validate minimum requirements
    num_entities = len(graph_data.get('entities', []))
    num_relationships = len(graph_data.get('relationships', []))
    logger.info(f"Extraction complete:")
    logger.info(f"  - Entities extracted: {num_entities}")
    logger.info(f"  - Relationships extracted: {num_relationships}")
    
    if num_entities < 20:
        logger.warning(f"⚠️  Only {num_entities} entities extracted. Target: 20+ entities")
    if num_relationships < 20:
        logger.warning(f"⚠️  Only {num_relationships} relationships extracted. Target: 20+ relationships")
    if num_entities >= 20 and num_relationships >= 20:
        logger.info("✅ Minimum requirements met: 20+ entities and 20+ relationships")

    # 4. Save JSON Output
    json_path = Config.get_output_path(Config.JSON_FILENAME)
    with open(json_path, 'w') as f:
        json.dump(graph_data, f, indent=2)
    logger.info(f"JSON data saved to {json_path}")

    # 5. Generate Visualization
    graph_path = Config.get_output_path(Config.GRAPH_FILENAME)
    GraphVisualizer.create_and_save_graph(graph_data, graph_path)
    
    logger.info("Mission Complete. Documentation and Demo required next.")

if __name__ == "__main__":
    main()