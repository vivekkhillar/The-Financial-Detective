# The Financial Detective

A Python application that extracts financial knowledge graphs from annual reports using LLM (Large Language Model) extraction. This project extracts entities (Company Names, Risk Factors, Dollar Amounts) and relationships from messy financial text and visualizes them as a knowledge graph.

## Requirements Met ✅

1. **Python Script** - Complete extraction pipeline (`main.py`)
2. **LLM-Based Extraction** - Uses LLM (no regex) for entity and relationship extraction
3. **Strict JSON Output** - Generates `graph_output.json` with valid JSON schema
4. **Visual Representation** - Creates `knowledge_graph.png` using NetworkX

## Project Structure

```
The Financial Detective/
├── main.py                 # Main entry point
├── src/
│   ├── __init__.py        # Auto path setup
│   ├── config.py          # Configuration settings
│   ├── data_loader.py     # Loads text from file/URL
│   ├── extractor.py       # LLM-based entity extraction
│   ├── llm_engine.py      # LLM API interface
│   ├── visualizer.py      # NetworkX graph visualization
│   └── utils.py           # Utility functions
├── data/
│   └── messy_text.txt     # Extracted text from PDF (5 pages)
├── output/
│   ├── graph_output.json  # Knowledge graph JSON output
│   └── knowledge_graph.png # Visual graph representation
├── PDF/
│   └── RIL-Integrated-Annual-Report-2024-25.pdf
└── requirements.txt       # Python dependencies
```

## Features

- **LLM-Based Extraction**: Uses local LLM (gemma3:12b) or GPT-4o for extraction
- **No Regex**: All extraction done through LLM understanding
- **Comprehensive Entities**: Extracts Companies, People, Financial Amounts, Risks, Frameworks
- **Rich Relationships**: Extracts ownership (OWNS), financial (HAS_PROFIT, HAS_REVENUE), personnel (EMPLOYS), etc.
- **Visual Graph**: Beautiful NetworkX visualization with color-coded nodes and labeled edges
- **Strict JSON Schema**: Valid JSON output following knowledge graph format

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. **Generate messy text file** (if not already done):
   ```bash
   python generate_messy_text.py
   ```

2. **Run the main script**:
   ```bash
   python main.py
   ```

3. **Outputs**:
   - `output/graph_output.json` - Knowledge graph in JSON format
   - `output/knowledge_graph.png` - Visual graph representation

## Configuration

Edit `src/config.py` to configure:
- LLM API URL and model name
- Input source (local file or URL)
- Output paths
- Extraction settings

## JSON Schema

The output follows this strict JSON schema:

```json
{
  "entities": [
    {
      "id": "entity_name",
      "type": "Company|Person|Dollar Amount|Risk|Framework|...",
      "metadata": "Additional context"
    }
  ],
  "relationships": [
    {
      "source": "entity_name",
      "target": "entity_name",
      "type": "OWNS|HAS_PROFIT|EMPLOYS|..."
    }
  ]
}
```

## Example Output

- **Entities**: Reliance Industries Limited, Mukesh D. Ambani, ₹81,309 crore (Profit), etc.
- **Relationships**: 
  - Reliance Retail → OWNS → Hamleys
  - RIL → HAS_PROFIT → ₹81,309 crore
  - Mukesh Ambani → REPORTS_TO → RIL

## Author

Vivek Khillar
