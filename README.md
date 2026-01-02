# The Financial Detective

A Python application that extracts financial knowledge graphs from annual reports using **100% LLM-based extraction** (no regex). This project extracts entities (Company Names, Risk Factors, Dollar Amounts) and relationships from messy financial text and visualizes them as a connected knowledge graph.

## 🎯 Project Overview

The Financial Detective processes unstructured financial text and extracts:
- **Entities**: Companies, People, Financial Amounts, Risks, Frameworks, Metrics, Locations, Products
- **Relationships**: Ownership (OWNS), Financial (HAS_PROFIT, HAS_REVENUE), Personnel (EMPLOYS, CHAIRMAN), Risks (FACES_RISK), and more
- **Visual Graph**: Interactive NetworkX visualization with color-coded nodes and labeled edges

## ✅ Requirements Met

1. **Python Script** - Complete extraction pipeline (`main.py`)
2. **LLM-Based Extraction** - Uses LLM exclusively (no regex) for entity and relationship extraction
3. **Strict JSON Output** - Generates `graph_output.json` with valid JSON schema
4. **Visual Representation** - Creates `knowledge_graph.png` using NetworkX with all edges connected
5. **Text Preprocessing** - Optional tokenization and chunking using string operations only (no regex)

## 📁 Project Structure

```
The-Financial-Detective/
├── main.py                      # Main entry point
├── generate_messy_text.py       # Script to generate messy text from PDF
├── src/
│   ├── __init__.py              # Auto path setup
│   ├── config.py                # Configuration settings
│   ├── data_loader.py           # Loads text from local file
│   ├── tokenizer.py             # Text preprocessing (string ops only, no regex)
│   ├── extractor.py             # LLM-based entity/relationship extraction
│   ├── llm_engine.py            # LLM API interface
│   ├── visualizer.py            # NetworkX graph visualization
│   └── utils.py                 # Utility functions
├── data/
│   └── messy_text.txt           # Input text file (extracted from PDF)
├── output/
│   ├── graph_output.json        # Knowledge graph JSON output
│   └── knowledge_graph.png      # Visual graph representation
├── PDF/
│   └── RIL-Integrated-Annual-Report-2024-25.pdf
├── tests/
│   └── test_extraction.py       # Unit tests
└── requirements.txt             # Python dependencies
```

## 🚀 Features

- **100% LLM-Based Extraction**: All entity and relationship extraction done through LLM understanding (no regex)
- **Text Preprocessing**: Optional tokenization and chunking using string operations only
- **Comprehensive Entities**: Extracts Companies, People, Financial Amounts, Risks, Frameworks, Metrics, etc.
- **Rich Relationships**: Extracts ownership (OWNS), financial (HAS_PROFIT, HAS_REVENUE), personnel (EMPLOYS, CHAIRMAN), risks (FACES_RISK), frameworks (FOLLOWS), and more
- **Connected Graph**: Ensures all nodes are connected with automatic edge creation for isolated nodes
- **Visual Graph**: Beautiful NetworkX visualization with:
  - Color-coded nodes by entity type
  - Labeled edges with relationship types
  - Dynamic sizing based on graph complexity
  - High-resolution output (300 DPI)
- **Strict JSON Schema**: Valid JSON output following knowledge graph format
- **Parallel Processing**: Optional parallel chunk processing for faster extraction
- **Minimum Requirements**: Targets 20+ entities and 20+ relationships

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd The-Financial-Detective
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure data file exists:**
   - Place your text file at `data/messy_text.txt`
   - Or run `python generate_messy_text.py` to extract text from PDF

## 🎮 Usage

### Basic Usage

1. **Generate messy text file** (if not already done):
   ```bash
   python generate_messy_text.py
   ```
   This extracts text from the PDF and saves it to `data/messy_text.txt`.

2. **Run the main script:**
   ```bash
   python main.py
   ```

3. **Check outputs:**
   - `output/graph_output.json` - Knowledge graph in JSON format
   - `output/knowledge_graph.png` - Visual graph representation

### Configuration

Edit `src/config.py` to configure:

- **LLM Settings:**
  - `LLM_API_URL` - LLM API endpoint
  - `LLM_MODEL_NAME` - Model name (e.g., "gemma3:12b")
  - `MAX_TOKENS` - Maximum tokens for LLM response
  - `temperature` - LLM temperature setting

- **Text Processing:**
  - `TOKENIZE_TEXT` - Enable/disable text tokenization
  - `CLEAN_TEXT` - Enable/disable text cleaning
  - `CHUNK_TEXT` - Enable/disable text chunking
  - `CHUNK_SIZE` - Maximum characters per chunk (default: 4000)
  - `CHUNK_OVERLAP` - Characters to overlap between chunks (default: 300)
  - `CHUNK_STRATEGY` - Chunking strategy: "sentence", "paragraph", or "fixed"

- **File Paths:**
  - `MESSY_TEXT_FILE` - Path to input text file
  - `OUTPUT_DIR` - Output directory for JSON and graph files

## 📊 JSON Schema

The output follows this strict JSON schema:

```json
{
  "entities": [
    {
      "id": "entity_name",
      "type": "Company|Person|Dollar Amount|Risk|Framework|Metric|Location|Product",
      "metadata": "Additional context or description"
    }
  ],
  "relationships": [
    {
      "source": "entity_name",
      "target": "entity_name",
      "relation": "OWNS|HAS_PROFIT|EMPLOYS|CHAIRMAN|FACES_RISK|FOLLOWS|..."
    }
  ]
}
```

### Entity Types

- **Company**: Organizations, subsidiaries, business units
- **Person**: Individuals (executives, founders, employees)
- **Dollar Amount**: Financial figures (revenue, profit, assets, etc.)
- **Risk**: Risk factors and challenges
- **Framework**: Standards and guidelines (GRI, UN SDGs, etc.)
- **Metric**: Rankings and measurements
- **Location**: Geographic locations
- **Product**: Products and services

### Relationship Types

- **OWNS**: Ownership relationships
- **SUBSIDIARY_OF**: Subsidiary relationships
- **HAS_PROFIT**, **HAS_REVENUE**, **HAS_ASSET**, **HAS_EQUITY**, **HAS_DEBT**: Financial relationships
- **EMPLOYS**, **CHAIRMAN**, **FOUNDER**, **CEO**, **DIRECTOR**: Personnel relationships
- **FACES_RISK**: Risk relationships
- **FOLLOWS**, **USES**: Framework relationships
- **RANKED_IN**: Ranking relationships
- **LOCATED_IN**: Location relationships
- **RELATED_TO**: General relationships

## 📈 Example Output

### Entities
- Reliance Industries Limited (Company)
- Mukesh D. Ambani (Person - Chairman)
- ₹81,309 crore (Dollar Amount - Net Profit)
- Hamleys (Company - Subsidiary)
- GRI Standards (Framework)

### Relationships
- `Reliance Industries Limited → OWNS → Hamleys`
- `Mukesh D. Ambani → CHAIRMAN → Reliance Industries Limited`
- `Reliance Industries Limited → HAS_PROFIT → ₹81,309 crore`
- `Reliance Industries Limited → FOLLOWS → GRI Standards`

## 🔧 Technical Details

### LLM Extraction
- **No Regex**: All extraction is done 100% by LLM
- **Strict JSON**: LLM is instructed to return valid JSON only
- **Chunking Support**: Large texts are processed in chunks with overlap
- **Parallel Processing**: Multiple chunks can be processed concurrently

### Text Preprocessing
- **String Operations Only**: No regex used in tokenizer
- **Minimal Cleaning**: Preserves original text structure
- **Flexible Chunking**: Supports sentence, paragraph, or fixed-size chunking

### Graph Visualization
- **Automatic Connection**: Isolated nodes are automatically connected to the main node
- **Color Coding**: Nodes colored by entity type, edges colored by relationship type
- **Dynamic Sizing**: Figure, node, and label sizes adjust based on graph complexity
- **High Quality**: 300 DPI output for clear visualization

## 🧪 Testing

Run tests to verify extraction:
```bash
pytest tests/
```

## 📝 Notes

- The project uses **no regex** for entity/relationship extraction (100% LLM-based)
- Text preprocessing uses string operations only (no regex)
- All nodes in the graph are guaranteed to be connected
- Minimum target: 20+ entities and 20+ relationships

## 👤 Author

**Vivek Khillar**

## 📄 License

[Add your license here]
