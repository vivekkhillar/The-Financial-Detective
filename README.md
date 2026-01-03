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
6. **Logging System** - Comprehensive logging to both console and file (`output/financial_detective.log`)

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
│   ├── knowledge_graph.png      # Visual graph representation
│   └── financial_detective.log  # Application log file
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
  - Automatic connection of isolated nodes to main entity
- **Strict JSON Schema**: Valid JSON output following knowledge graph format
- **Comprehensive Logging**: Dual output to console and log file with timestamps
- **Robust Error Handling**: Graceful handling of missing nodes, invalid JSON, and API errors
- **Minimum Requirements**: Targets 20+ entities and 20+ relationships with validation

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
   - `output/financial_detective.log` - Application execution log

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
  - `OUTPUT_DIR` - Output directory for JSON, graph, and log files
  - `LOG_FILENAME` - Log file name (default: "financial_detective.log")

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

- **OWNS**: Ownership relationships (e.g., Reliance Retail OWNS Hamleys)
- **SUBSIDIARY_OF**: Subsidiary relationships
- **ACQUIRED**: Acquisition relationships
- **HAS_PROFIT**, **HAS_REVENUE**, **HAS_ASSET**, **HAS_EQUITY**, **HAS_DEBT**, **HAS_EXPORTS**, **HAS_CSR_CONTRIBUTION**: Financial relationships
- **EMPLOYS**, **CHAIRMAN**, **FOUNDER**, **CEO**, **MANAGING_DIRECTOR**, **DIRECTOR**, **REPORTS_TO**: Personnel relationships
- **FACES_RISK**: Risk relationships
- **FOLLOWS**, **USES**: Framework relationships
- **RANKED_IN**: Ranking relationships
- **LOCATED_IN**: Location relationships
- **OPERATES**: Operational relationships
- **INVESTED_IN**: Investment relationships
- **PARTNERS_WITH**: Partnership relationships
- **COMPETES_WITH**: Competitive relationships
- **IMPACTS**: Impact relationships
- **RELATED_TO**: General relationships (used for auto-connecting isolated nodes)

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
- **Automatic Connection**: Isolated nodes are automatically connected to the main node (typically the primary company)
- **Color Coding**: 
  - Nodes colored by entity type (Company=Blue, Person=Light Blue, Dollar Amount=Green, Risk=Red, Framework=Purple, etc.)
  - Edges colored by relationship type (Ownership=Red, Financial=Green, Personnel=Blue, Risk=Orange, Framework=Purple)
- **Dynamic Sizing**: Figure, node, and label sizes adjust based on graph complexity
- **High Quality**: 300 DPI output for clear visualization
- **Edge Labels**: All relationship types displayed on edges with formatted labels
- **Node Metadata**: Entity metadata preserved and available in graph structure
- **Missing Node Handling**: Automatically creates nodes for entities referenced in relationships but not explicitly defined

## 🧪 Testing

Run tests to verify extraction:
```bash
pytest tests/
```

## 📝 Current Project Status

### ✅ Implemented Features
- ✅ 100% LLM-based entity and relationship extraction (no regex)
- ✅ Text preprocessing with string operations only (no regex)
- ✅ Comprehensive entity extraction (9 entity types)
- ✅ Rich relationship extraction (25+ relationship types)
- ✅ Automatic graph connection (all nodes guaranteed to be connected)
- ✅ Dual logging (console + file)
- ✅ Robust error handling and JSON validation
- ✅ High-quality graph visualization (300 DPI)
- ✅ Missing node auto-creation from relationships
- ✅ Minimum requirements validation (20+ entities/relationships)

### 📊 Current Capabilities
- **Entity Types**: Company, Person, Location, Dollar Amount, Risk, Product, Framework, Metric, Subsidiary, Partnership
- **Relationship Types**: 25+ types including OWNS, HAS_PROFIT, CHAIRMAN, FOUNDER, FACES_RISK, FOLLOWS, etc.
- **Graph Features**: Color-coded nodes/edges, labeled relationships, automatic isolation handling
- **Processing**: Supports chunking, parallel processing, and flexible text preprocessing

### 🔄 Notes
- The project uses **no regex** for entity/relationship extraction (100% LLM-based)
- Text preprocessing uses string operations only (no regex)
- All nodes in the graph are guaranteed to be connected
- Minimum target: 20+ entities and 20+ relationships
- Logs are appended to file (not overwritten) for historical tracking

## 👤 Author

**Vivek Khillar**

## 📄 License

[Add your license here]
