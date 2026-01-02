import json
from .llm_engine import LLMEngine
from .utils import setup_logger, clean_json_string

logger = setup_logger()

class FinancialDetective:
    def __init__(self):
        self.llm = LLMEngine()

    def get_extraction_prompt(self):
        return """
        You are an expert Financial Knowledge Graph Extractor. Analyze the provided financial text and extract comprehensive entities and relationships into a structured JSON format.
        
        CRITICAL RULES:
        1. Output ONLY valid JSON - no markdown, no explanations, no text before or after
        2. Extract ALL relevant information: be thorough and comprehensive
        3. Include detailed metadata for entities when available
        4. Identify ALL relationships mentioned in the text
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
        
        DETAILED EXTRACTION REQUIREMENTS:
        1. **CRITICAL: Extract ALL company names - be extremely thorough**
           - Extract ALL company names mentioned: parent companies, subsidiaries, joint ventures, associates, business units
           - Extract business segment names (e.g., Reliance Retail, Reliance Jio, Reliance Petroleum, etc.)
           - Extract subsidiary company names explicitly mentioned
           - Extract acquired company names
           - Extract joint venture partner names
           - Extract brand names and business divisions
           - **PRIORITY: Focus on companies owned by or related to RIL (Reliance Industries Limited)**
        
        2. **CRITICAL: Extract ALL companies that RIL OWNS**
           - If text mentions "RIL owns X" or "Reliance owns X" → extract OWNS relationship
           - If text mentions "subsidiary" or "subsidiaries" → extract all subsidiary names and create OWNS relationships
           - If text mentions "Reliance Retail", "Reliance Jio", "Reliance Petroleum", "Jio Platforms", etc. → extract as companies and create OWNS relationship from RIL
           - If text mentions "100% owned" or "wholly owned" → extract OWNS relationship
           - If text mentions "acquired" or "acquisition" → extract ACQUIRED relationship
           - Extract ALL business segments and divisions as separate companies if they are distinct entities
           - **Example: "Reliance Retail owns Hamleys" → Extract both "Reliance Retail" and "Hamleys" as companies, create OWNS relationship from RIL to Reliance Retail, and from Reliance Retail to Hamleys**
        
        3. **CRITICAL: Extract ALL Risk Factors**
           - Extract ALL risk factors mentioned (market risks, operational risks, regulatory risks, financial risks, etc.)
           - Extract risk descriptions and categories
           - **ALWAYS create FACES_RISK relationship** linking RIL (or relevant company) to each risk factor
           - Include risk descriptions in metadata
           - Examples: "Market volatility", "Regulatory changes", "Currency fluctuations", "Competition", "Supply chain disruptions", etc.
        
        4. **CRITICAL: Extract ALL financial figures with FULL context - especially PROFIT amounts**
           - Extract ALL profit amounts mentioned (Net Profit, Cash Profit, Profit After Tax, Operating Profit, etc.)
           - Extract profit figures with their context (e.g., "Net Profit: ₹81,309 crore" → entity: "₹81,309 crore", type: "Dollar Amount", metadata: "Net Profit FY 2024-25")
           - Extract ALL revenue amounts (e.g., "Revenue of ₹10,71,174 crore")
           - Extract ALL asset, debt, equity amounts with their context
           - **ALWAYS create HAS_PROFIT relationship** linking RIL (or relevant company) to profit amount
           - **ALWAYS create HAS_REVENUE relationship** linking company to revenue amount
           - **ALWAYS create HAS_ASSET/HAS_EQUITY/HAS_DEBT relationships** for financial amounts
           - Include financial year/period in metadata (e.g., "FY 2024-25", "Y-o-Y")
           - **PRIORITY: Extract profit amounts and link them to RIL with HAS_PROFIT relationship**
        
        5. **CRITICAL: Extract relationships from metadata and descriptive text**
           - If metadata says "Founder is Dhirubhai H. Ambani" → create relationship: {"source": "Dhirubhai H. Ambani", "target": "RIL", "relation": "FOUNDER"}
           - If metadata says "Chairman and Managing Director" → create relationship: {"source": "Person", "target": "Company", "relation": "CHAIRMAN"} or {"source": "Person", "target": "Company", "relation": "MANAGING_DIRECTOR"}
           - If metadata mentions a role (CEO, Director, Founder, etc.) → create appropriate relationship
           - If text says "Company X's revenue" or "Company X reported profit" → create HAS_REVENUE/HAS_PROFIT relationship
           - If text says "Company X operates in Location Y" → create OPERATES relationship
           - **Link ALL entities to the main company (RIL) when contextually appropriate**
        
        6. **CRITICAL: Extract ALL ownership relationships (who owns which company)**
           - If text mentions "Company A owns Company B" or "Company A is parent of Company B" → extract OWNS relationship
           - If text mentions "Company A subsidiary Company B" → extract SUBSIDIARY_OF relationship
           - If text mentions "Company A acquired Company B" → extract ACQUIRED relationship
           - If text mentions "Company A holds X% stake in Company B" → extract OWNS relationship with metadata
           - Extract ownership percentages when mentioned (e.g., "51% stake", "100% ownership")
           - Extract all subsidiaries, joint ventures, and associates mentioned
           - **PRIORITY: Focus on RIL's ownership of other companies**
        
        7. Extract ALL locations and link companies to locations with LOCATED_IN or OPERATES relationship
        8. Extract ALL financial metrics and link them to companies with appropriate relationships
        9. Extract ALL partnerships, joint ventures, and collaborations with PARTNERS_WITH relationship
        10. Include metadata for entities: roles, descriptions, values, dates, ownership percentages when available
        11. **IMPORTANT: Create relationships from ANY descriptive information, not just explicit statements**
            - "Founder is X" → FOUNDER relationship
            - "Chairman is X" → CHAIRMAN relationship  
            - "Revenue of Y" → HAS_REVENUE relationship
            - "Profit of Z" → HAS_PROFIT relationship
            - "Located in L" → LOCATED_IN relationship
            - "Operates in S" → OPERATES relationship
        12. Be comprehensive - extract as many entities and relationships as possible
        
        OWNERSHIP EXTRACTION PRIORITY (RIL's Companies):
        - **HIGHEST PRIORITY: Extract ALL companies owned by RIL**
        - Extract ALL subsidiaries of RIL (Reliance Retail, Reliance Jio, Jio Platforms, Reliance Petroleum, etc.)
        - Extract ALL companies acquired by RIL
        - Extract ALL joint ventures where RIL is a partner
        - Extract ALL business segments and divisions as separate companies
        - **Create OWNS relationship from RIL to each subsidiary/company it owns**
        - Extract ownership percentages in metadata when available
        - Examples:
          - "Reliance Retail" → Entity: "Reliance Retail", Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Reliance Retail", "relation": "OWNS"}
          - "Reliance Jio" → Entity: "Reliance Jio", Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Reliance Jio", "relation": "OWNS"}
          - "Reliance Retail owns 100% of Hamleys" → 
            Entity: "Hamleys" with metadata "100% owned by Reliance Retail"
            Relationship: {"source": "Reliance Retail", "target": "Hamleys", "relation": "OWNS"}
            Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Reliance Retail", "relation": "OWNS"}
        
        RISK FACTOR EXTRACTION PRIORITY:
        - Extract ALL risk factors mentioned in the text
        - Look for sections titled "Risk Factors", "Risks", "Challenges", "Threats"
        - Extract market risks, operational risks, regulatory risks, financial risks, strategic risks
        - **ALWAYS create FACES_RISK relationship from RIL to each risk factor**
        - Include risk category and description in metadata
        
        PROFIT AMOUNT EXTRACTION PRIORITY:
        - Extract ALL profit figures mentioned (Net Profit, Cash Profit, PAT, Operating Profit, etc.)
        - Look for phrases like "profit of", "net profit", "earnings", "income"
        - **ALWAYS create HAS_PROFIT relationship from RIL to profit amount**
        - Include profit type and financial year in metadata
        
        REQUIRED JSON FORMAT (output this exact structure):
        {
          "entities": [
            {
              "id": "entity_name",
              "type": "Company|Person|Location|Dollar Amount|Risk|Product|Framework|Metric|Subsidiary|Partnership",
              "metadata": "Detailed description, role, value, or context"
            }
          ],
          "relationships": [
            {
              "source": "entity_name",
              "target": "entity_name",
              "relation": "OWNS|OPERATES|EMPLOYS|REPORTS_TO|FOUNDER|CHAIRMAN|MANAGING_DIRECTOR|CEO|DIRECTOR|LOCATED_IN|FACES_RISK|HAS_REVENUE|HAS_PROFIT|HAS_ASSET|HAS_EQUITY|HAS_DEBT|HAS_EXPORTS|HAS_CSR_CONTRIBUTION|INVESTED_IN|PARTNERS_WITH|SUBSIDIARY_OF|RANKED_IN|FOLLOWS|USES|IMPACTS|COMPETES_WITH|ACQUIRED"
            }
          ]
        }
        
        CRITICAL: EXTRACT RELATIONSHIPS FROM METADATA AND DESCRIPTIVE TEXT:
        - If metadata says "Founder is Dhirubhai H. Ambani" or "Founder Chairman" → 
          Create relationship: {"source": "Dhirubhai H. Ambani", "target": "Reliance Industries Limited (RIL)", "relation": "FOUNDER"}
        - If metadata says "Chairman and Managing Director" → 
          Create relationship: {"source": "Person", "target": "RIL", "relation": "CHAIRMAN"} AND {"source": "Person", "target": "RIL", "relation": "MANAGING_DIRECTOR"}
        - If metadata says "Consolidated Total Equity" for an amount → 
          Create relationship: {"source": "RIL", "target": "Amount", "relation": "HAS_EQUITY"}
        - If metadata says "Exports" for an amount → 
          Create relationship: {"source": "RIL", "target": "Amount", "relation": "HAS_EXPORTS"}
        - If metadata says "CSR Contribution" → 
          Create relationship: {"source": "RIL", "target": "Amount", "relation": "HAS_CSR_CONTRIBUTION"}
        - If metadata says "Net Profit" or "Profit" → 
          Create relationship: {"source": "RIL", "target": "Amount", "relation": "HAS_PROFIT"}
        - **ALWAYS link entities to RIL when metadata or context indicates a relationship**
        - **Extract relationships from ANY descriptive information, not just explicit statements**
        
        EXAMPLES:
        - "Reliance Retail owns Hamleys" → 
          Entity: {"id": "Hamleys", "type": "Company", "metadata": "Owned by Reliance Retail"}
          Relationship: {"source": "Reliance Retail", "target": "Hamleys", "relation": "OWNS"}
        
        - "Founder is Dhirubhai H. Ambani" (from metadata) → 
          Entity: {"id": "Dhirubhai H. Ambani", "type": "Person", "metadata": "Founder Chairman"}
          Relationship: {"source": "Dhirubhai H. Ambani", "target": "Reliance Industries Limited (RIL)", "relation": "FOUNDER"}
        
        - "Chairman and Managing Director" (from metadata) → 
          Entity: {"id": "Mukesh D. Ambani", "type": "Person", "metadata": "Chairman and Managing Director"}
          Relationship: {"source": "Mukesh D. Ambani", "target": "Reliance Industries Limited (RIL)", "relation": "CHAIRMAN"}
          Relationship: {"source": "Mukesh D. Ambani", "target": "Reliance Industries Limited (RIL)", "relation": "MANAGING_DIRECTOR"}
        
        - "Consolidated Total Equity: ₹10,00,000 Crore" → 
          Entity: {"id": "₹10,00,000 Crore", "type": "Dollar Amount", "metadata": "Consolidated Total Equity"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "₹10,00,000 Crore", "relation": "HAS_EQUITY"}
        
        - "RIL reported revenue of ₹10,71,174 crore" → 
          Entity: {"id": "₹10,71,174 crore", "type": "Dollar Amount", "metadata": "Revenue FY 2024-25"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "₹10,71,174 crore", "relation": "HAS_REVENUE"}
        
        - "RIL faces market volatility risk" → 
          Entity: {"id": "Market Volatility", "type": "Risk", "metadata": "Market risk factor"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Market Volatility", "relation": "FACES_RISK"}
        
        - "RIL owns Reliance Retail" or "Reliance Retail is a subsidiary of RIL" → 
          Entity: {"id": "Reliance Retail", "type": "Company", "metadata": "Subsidiary of RIL"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Reliance Retail", "relation": "OWNS"}
        
        - "RIL reported Net Profit of ₹81,309 crore" → 
          Entity: {"id": "₹81,309 crore", "type": "Dollar Amount", "metadata": "Net Profit FY 2024-25"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "₹81,309 crore", "relation": "HAS_PROFIT"}
        
        - "Risk factors include regulatory changes and market volatility" → 
          Entity: {"id": "Regulatory Changes", "type": "Risk", "metadata": "Regulatory risk factor"}
          Entity: {"id": "Market Volatility", "type": "Risk", "metadata": "Market risk factor"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Regulatory Changes", "relation": "FACES_RISK"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Market Volatility", "relation": "FACES_RISK"}
        
        - "Reliance Jio, Reliance Retail, Jio Platforms are subsidiaries" → 
          Entity: {"id": "Reliance Jio", "type": "Company", "metadata": "Subsidiary of RIL"}
          Entity: {"id": "Jio Platforms", "type": "Company", "metadata": "Subsidiary of RIL"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Reliance Jio", "relation": "OWNS"}
          Relationship: {"source": "Reliance Industries Limited (RIL)", "target": "Jio Platforms", "relation": "OWNS"}
        
        CRITICAL FORMAT REQUIREMENTS - FOLLOW EXACTLY:
        - Start your response with { and end with }
        - Use "id" field for entity names (NOT "name", NOT "entity_name")
        - Use "metadata" field for descriptions (NOT "description", NOT "desc")
        - Use "source" and "target" in relationships (NOT "entity1" and "entity2", NOT "from" and "to")
        - Use "relation" field in relationships (NOT "type", NOT "relationship", NOT "rel")
        - **USE STANDARDIZED RELATION TYPES**: OWNS, HAS_PROFIT, HAS_REVENUE, HAS_EQUITY, FACES_RISK, CHAIRMAN, FOUNDER, etc.
        - DO NOT use descriptive text like "Business Segment", "Reached Consolidated Total Equity" - use standardized types like OWNS, HAS_EQUITY
        - DO NOT create separate sections like "financial_data", "financials", "awards_and_recognitions", "metrics", "metadata"
        - ALL entities MUST be in the "entities" array
        - ALL relationships MUST be in the "relationships" array
        - Extract as many entities and relationships as possible
        - Include detailed metadata for better context
        - Do not include any text, markdown, or explanations outside the JSON
        
        MANDATORY EXTRACTIONS:
        1. Extract ALL company names mentioned (Reliance Retail, Reliance Jio, Jio Platforms, etc.) as separate Company entities
        2. Extract ALL risk factors mentioned in the text as Risk entities
        3. Extract ALL profit amounts (Net Profit, Cash Profit, etc.) as Dollar Amount entities with HAS_PROFIT relationships
        4. Create OWNS relationships from RIL to all subsidiaries and companies it owns
        5. Create FACES_RISK relationships from RIL to all risk factors
        
        EXAMPLE OF CORRECT FORMAT:
        {
          "entities": [
            {"id": "Reliance Industries Limited", "type": "Company", "metadata": "India's largest private sector enterprise"},
            {"id": "Mukesh D. Ambani", "type": "Person", "metadata": "Chairman and Managing Director"},
            {"id": "₹81,309 crore", "type": "Dollar Amount", "metadata": "Net Profit FY 2024-25"}
          ],
          "relationships": [
            {"source": "Mukesh D. Ambani", "target": "Reliance Industries Limited", "relation": "CHAIRMAN"},
            {"source": "Reliance Industries Limited", "target": "₹81,309 crore", "relation": "HAS_PROFIT"}
          ]
        }
        """

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