import json
from .llm_engine import LLMEngine
from .utils import setup_logger, clean_json_string

logger = setup_logger()

class FinancialDetective:
    
    def __init__(self):
        self.llm = LLMEngine()

    def get_extraction_prompt(self):
        return """
        You are an expert Financial Knowledge Graph Extractor. Analyze the provided financial text and extract entities and relationships into a structured JSON format.
        
        CRITICAL RULES:
        1. Output ONLY valid JSON - no markdown, no explanations, no text before or after
        2. Extract ALL relevant information that is explicitly mentioned in the text
        3. Include metadata for entities when available
        4. Identify relationships mentioned in the text
        5. Use the EXACT schema below - no variations
        
        ENTITY TYPES TO EXTRACT:
        - Company: All company names, subsidiaries, joint ventures, associates
        - Person: Key personnel (CEOs, Chairmen, Directors, Founders, Executives)
        - Location: Countries, cities, regions mentioned
        - Dollar Amount: All financial figures (revenue, profit, assets, debt, investments, etc.) with context
        - Risk: Risk factors, challenges, threats mentioned
        - Product: Products, services, brands mentioned
        - Framework: Standards, guidelines, certifications (GRI, ISO, etc.)
        - Metric: KPIs, ratios, percentages (ROE, ROCE, debt-to-equity, etc.)
        - Subsidiary: Subsidiary companies and their relationships
        - Partnership: Joint ventures, partnerships, collaborations
        
        RELATIONSHIP TYPES TO IDENTIFY:
        - OWNS: Company ownership (e.g., Reliance Retail OWNS Hamleys)
        - OPERATES: Company operates in location/industry
        - EMPLOYS: Company employs person
        - REPORTS_TO: Person reports to person/company
        - FOUNDER: Person is founder of company (e.g., Dhirubhai H. Ambani FOUNDER RIL)
        - CHAIRMAN: Person is chairman of company
        - MANAGING_DIRECTOR: Person is managing director of company
        - CEO: Person is CEO of company
        - DIRECTOR: Person is director of company
        - LOCATED_IN: Entity located in location
        - FACES_RISK: Company faces specific risk
        - HAS_REVENUE: Company has revenue amount
        - HAS_PROFIT: Company has profit amount
        - HAS_ASSET: Company has asset value
        - HAS_EQUITY: Company has equity value
        - HAS_DEBT: Company has debt amount
        - HAS_EXPORTS: Company has export value
        - HAS_CSR_CONTRIBUTION: Company has CSR contribution amount
        - INVESTED_IN: Company invested in entity
        - PARTNERS_WITH: Company partners with company
        - SUBSIDIARY_OF: Company is subsidiary of company
        - RANKED_IN: Company ranked in ranking/list
        - FOLLOWS: Company follows framework/standard
        - USES: Company uses framework/standard
        - IMPACTS: Action/entity impacts metric/amount
        - COMPETES_WITH: Company competes with company
        - ACQUIRED: Company acquired company
        
        EXTRACTION REQUIREMENTS:
        1. Extract company names, subsidiaries, and business units
        2. Extract key personnel (CEOs, Chairmen, Directors, Founders)
        3. Extract financial amounts (revenue, profit, assets, debt, equity)
        4. Extract risk factors mentioned in the text
        5. Extract locations, products, frameworks, and metrics
        6. Create relationships between entities (OWNS, HAS_PROFIT, CHAIRMAN, etc.)
        
        REQUIRED JSON FORMAT:
        {
          "entities": [
            {
              "id": "entity_name",
              "type": "Company|Person|Location|Dollar Amount|Risk|Product|Framework|Metric",
              "metadata": "Description or context"
            }
          ],
          "relationships": [
            {
              "source": "entity_name",
              "target": "entity_name",
              "relation": "OWNS|HAS_PROFIT|CHAIRMAN|FOUNDER|OPERATES|EMPLOYS|LOCATED_IN|FACES_RISK|HAS_REVENUE|HAS_ASSET|HAS_EQUITY|HAS_DEBT"
            }
          ]
        }
        
        EXAMPLES:
        - "Reliance Retail owns Hamleys" → 
          Entity: {"id": "Hamleys", "type": "Company", "metadata": "Owned by Reliance Retail"}
          Relationship: {"source": "Reliance Retail", "target": "Hamleys", "relation": "OWNS"}
        
        - "Mukesh D. Ambani is Chairman" → 
          Entity: {"id": "Mukesh D. Ambani", "type": "Person", "metadata": "Chairman"}
          Relationship: {"source": "Mukesh D. Ambani", "target": "Reliance Industries Limited", "relation": "CHAIRMAN"}
        
        - "Net Profit: ₹81,309 crore" → 
          Entity: {"id": "₹81,309 crore", "type": "Dollar Amount", "metadata": "Net Profit"}
          Relationship: {"source": "Reliance Industries Limited", "target": "₹81,309 crore", "relation": "HAS_PROFIT"}
        """

        # return """
        #       You are the "Financial Detective," an elite AI specialized in extracting Knowledge Graphs from messy, OCR-scanned financial documents (Annual Reports).

        #       **YOUR GOAL:**
        #       Convert raw, noisy text into a pristine, structured JSON Knowledge Graph.

        #       **CRITICAL DATA CLEANING RULES:**
        #       1. **Ignore Noise:** Disregard page headers (e.g., "Integrated Report 2024-25"), page numbers, and decorative text.
        #       2. **Merge Synonyms (Entity Resolution):** - If the text says "RIL", "Reliance", or "the Company", normalize the ID to the full official name: "Reliance Industries Limited".
        #         - Treat "Jio", "RJIL", and "Reliance Jio" as "Reliance Jio Infocomm Limited".
        #       3. **Fix OCR Errors:** If text is broken (e.g., "Re venue"), infer the correct word ("Revenue").

        #       **SCHEMA INSTRUCTIONS:**
        #       You must output a JSON object with two lists: "entities" and "relationships".

        #       **Entity Types:**
        #       - "Company" (e.g., Reliance Retail, Hamleys)
        #       - "Person" (e.g., Mukesh Ambani)
        #       - "Metric" (Financial figures treated as nodes, e.g., "₹ 10,000 Cr", "25% Growth")
        #       - "Risk" (Specific threats, e.g., "Supply Chain Volatility")
        #       - "Location" (Cities, Countries)

        #       **Allowed Relationships (Strict List):**
        #       OWNS, OPERATES_IN, LEADS (for executives), REPORTED_REVENUE, REPORTED_PROFIT, FACES_RISK, ACQUIRED, PARTNERED_WITH, SUBSIDIARY_OF

        #       **OUTPUT FORMAT (Strict JSON Only):**
        #       {
        #         "entities": [
        #           {"id": "Reliance Industries Limited", "type": "Company", "desc": "Parent conglomerate"},
        #           {"id": "Mukesh Ambani", "type": "Person", "desc": "Chairman & MD"},
        #           {"id": "₹ 9,000 Cr", "type": "Metric", "desc": "Net Profit Q3"}
        #         ],
        #         "relationships": [
        #           {"source": "Mukesh Ambani", "target": "Reliance Industries Limited", "relation": "LEADS"},
        #           {"source": "Reliance Industries Limited", "target": "₹ 9,000 Cr", "relation": "REPORTED_PROFIT"}
        #         ]
        #       }
        #       """

    def analyze(self, raw_text):
        prompt = self.get_extraction_prompt()
        raw_response = self.llm.generate_extraction(prompt, raw_text)
        
        # Post-process the response
        cleaned_response = clean_json_string(raw_response)
        
        try:
            data = json.loads(cleaned_response)
            # Basic validation
            if "entities" not in data or "relationships" not in data:
                logger.warning("JSON missing required keys, using empty structure")
                return {"entities": [], "relationships": []}
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON. LLM returned: {raw_response[:200]}...")
            logger.warning("Returning empty knowledge graph structure")
            # Return empty structure instead of crashing
            return {"entities": [], "relationships": []}