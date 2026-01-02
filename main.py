import json
# Path setup happens automatically when src is imported (see src/__init__.py)
from src.config import Config
from src.data_loader import PDFLoader
from src.extractor import FinancialDetective
from src.visualizer import GraphVisualizer
from src.utils import setup_logger

def main():
    logger = setup_logger()
    logger.info("Starting The Financial Detective...")

    # 1. Fetch Data (from local file or URL based on Config.USE_LOCAL_FILE)
    loader = PDFLoader()
    raw_text = loader.fetch_and_parse()

    # 2. Extract Info via LLM
    detective = FinancialDetective()
    graph_data = detective.analyze(raw_text)

    # 3. Save JSON Output
    json_path = Config.get_output_path(Config.JSON_FILENAME)
    with open(json_path, 'w') as f:
        json.dump(graph_data, f, indent=2)
    logger.info(f"JSON data saved to {json_path}")

    # 4. Generate Visualization
    graph_path = Config.get_output_path(Config.GRAPH_FILENAME)
    GraphVisualizer.create_and_save_graph(graph_data, graph_path)
    
    logger.info("Mission Complete. Documentation and Demo required next.")

if __name__ == "__main__":
    main()