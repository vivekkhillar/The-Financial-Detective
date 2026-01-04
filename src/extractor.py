import json
import time
from .llm_engine import LLMEngine
from .utils import setup_logger, clean_json_string
from .config import Config

logger = setup_logger()

class FinancialDetective:
    
    def __init__(self):
        self.llm = LLMEngine()

    def get_extraction_prompt(self, existing_entities=None):
        """
        Generate extraction prompt, optionally with context about already extracted entities.
        """
        existing_context = ""
        if existing_entities and len(existing_entities) > 0:
            # Show first few entities to give context
            sample_entities = list(existing_entities)[:10]
            existing_context = f"""
            IMPORTANT - AVOID DUPLICATES:
            The following entities have already been extracted in previous chunks. DO NOT extract them again unless you find NEW information:
            {', '.join(sample_entities)}
            ... and {len(existing_entities) - len(sample_entities)} more entities.

            Focus on extracting ONLY NEW entities and relationships that haven't been extracted yet.
            """
        
        return f"""
          You are an expert Financial Knowledge Graph Extractor. Extract entities and relationships from the financial text below.

          ⛔ CRITICAL RULES:
          1. Output ONLY valid JSON - no markdown code blocks, no explanations, no text before or after
          2. Start with {{ and end with }}
          3. Extract ONLY NEW information - avoid extracting entities/relationships already extracted
          4. Use the EXACT schema below - no variations
          5. Focus on entities and relationships that are clearly mentioned in THIS text segment
          {existing_context}
          6. ⚠️ CRITICAL: MUST extract Company -> OWNS -> Company relationships when mentioned:
             - If text says "subsidiary", "owns", "acquired", "stake in", "business unit", "division" → extract OWNS relationship
             - Examples: "Reliance Industries Limited owns Jio" → Reliance Industries Limited -> OWNS -> Jio
             - Examples: "Reliance Retail is a subsidiary" → Reliance Industries Limited -> OWNS -> Reliance Retail
             - Examples: "Hamleys is owned by Reliance" → Reliance Industries Limited -> OWNS -> Hamleys
          7. RIL / Reliance / Reliance Industries Limited are same company - extract only ONE as "Reliance Industries Limited"
          8. Person names: "Shri Dhirubhai Ambani" = "Shri. Dhirubhai H. Ambani" = "Dhirubhai H. Ambani" - extract only ONE (use "Dhirubhai H. Ambani" without title)
          9. Person names: "Mukesh D. Ambani" = "Shri Mukesh D. Ambani" - extract only ONE (use "Mukesh D. Ambani" without title)
          10. DO NOT extract dates (FY 2024-25, CY24, March 31, 2025) as entities
          11. DO NOT extract events (Mahakumbh, festivals) as entities
          12. DO NOT extract documents (Annual Report) as entities
          13. Focus on Companies, People, Dollar Amounts, and Risks only
          14. Focus max 3 entites and 3 relationships during extraction
                
        ENTITY TYPES TO EXTRACT (BE PRECISE):
        - Company: All company names, subsidiaries, joint ventures, associates, business units, divisions
          ⚠️ IMPORTANT: When you see a company name mentioned as a subsidiary, business unit, or division of another company, 
            extract BOTH companies AND create an OWNS relationship between them
        - Person: Key personnel (Founders, Managing Directors) - use names WITHOUT titles (e.g., "Mukesh D. Ambani" NOT "Shri Mukesh D. Ambani", "Dhirubhai H. Ambani" NOT "Shri Dhirubhai Ambani")
        - Dollar Amount: ONLY financial figures with currency symbols (₹, $, L, J) and units (crore, million, billion)
        - Risk: Risk factors, challenges, threats (e.g., "Market volatility risk", "Regulatory compliance risk")
        - Extract maximum 5 entities and 5 relationships

        ⛔ DO NOT EXTRACT AS ENTITIES (CRITICAL):
        - Dates: "March 31, 2025", "FY 2024-25", "CY24", "2024", "2025" - these are NOT entities
        - Events: "Mahakumbh", festivals, ceremonies - these are NOT entities
        - Documents: "Annual Report", "Integrated Report" - these are NOT entities
        - Locations: "India", cities, countries - only extract if mentioned with financial data
        - Percentages: "5.7%", "10%" - these are metrics, not dollar amounts
        - Fiscal years: "FY 2024-25" - this is a date, NOT an entity
        - Dhirubhai H. Ambani: this is a person, NOT an entity and shri Dhirubhai H. Ambani and Dhirubhai H. Ambani both are same person.

        RELATIONSHIP TYPES TO IDENTIFY (IMPORTANT - CORRECT DIRECTION):
        - ⚠️ OWNS: Company -> OWNS -> Company (HIGHEST PRIORITY - extract whenever mentioned!)
          Examples: 
          * "Reliance Industries Limited owns Jio" → Reliance Industries Limited -> OWNS -> Jio
          * "Reliance Retail is a subsidiary" → Reliance Industries Limited -> OWNS -> Reliance Retail
          * "Hamleys is owned by Reliance" → Reliance Industries Limited -> OWNS -> Hamleys
          * "Reliance has a stake in Disney" → Reliance Industries Limited -> OWNS -> Disney
          * "Digital Services division" → Reliance Industries Limited -> OWNS -> Digital Services
          * "Oil and Gas business unit" → Reliance Industries Limited -> OWNS -> Oil and Gas
        - FOUNDER: Person -> FOUNDER -> Company (e.g., Shri Dhirubhai H. Ambani -> FOUNDER -> Reliance Industries Limited)
        - MANAGING_DIRECTOR: Person -> MANAGING_DIRECTOR -> Company
        - FACES_RISK: Company -> FACES_RISK -> Risk Factor
        - HAS_REVENUE: Company -> HAS_REVENUE -> Dollar Amount (NOT the reverse!)
        - HAS_PROFIT: Company -> HAS_PROFIT -> Dollar Amount (NOT the reverse!)
        - HAS_ASSET: Company -> HAS_ASSET -> Dollar Amount (NOT the reverse!)
        - HAS_EQUITY: Company -> HAS_EQUITY -> Dollar Amount (NOT the reverse!)
        - HAS_DEBT: Company -> HAS_DEBT -> Dollar Amount (NOT the reverse!)
        - HAS_EXPORTS: Company -> HAS_EXPORTS -> Dollar Amount (NOT the reverse!)
        - HAS_CSR_CONTRIBUTION: Company -> HAS_CSR_CONTRIBUTION -> Dollar Amount (NOT the reverse!)

        CRITICAL - RELATIONSHIP DIRECTIONS:
        - Financial relationships (HAS_REVENUE, HAS_PROFIT, etc.) ALWAYS go: Company -> relation -> Dollar Amount
        - NEVER: Dollar Amount -> HAS_REVENUE -> Company (WRONG!)
        - NEVER: Company -> HAS_REVENUE -> Person (WRONG! Persons cannot be financial amounts)
        - NEVER: Company -> HAS_PROFIT -> Person (WRONG! Persons cannot be financial amounts)
        - ONLY Companies can have financial relationships (HAS_REVENUE, HAS_PROFIT, etc.)
        - Financial relationships can ONLY target Dollar Amount or Metric entities, NEVER Person, Company, Location, etc.
        - Events, Dates, Locations, Persons CANNOT be targets of financial relationships
        
        EXTRACTION REQUIREMENTS:
        1. Extract company names, subsidiaries, and business units (NOT dates, NOT events)
        2. ⚠️ CRITICAL PRIORITY: Extract Company -> OWNS -> Company relationships:
           - Look for keywords: "subsidiary", "owns", "owned by", "acquired", "stake in", "business unit", "division", "segment"
           - Extract BOTH companies as entities
           - Create OWNS relationship: Parent Company -> OWNS -> Subsidiary/Unit
           - Examples: 
             * "Jio is a subsidiary of Reliance" → Extract: Jio (Company), Reliance Industries Limited (Company), Reliance Industries Limited -> OWNS -> Jio
             * "Reliance Retail division" → Extract: Reliance Retail (Company), Reliance Industries Limited -> OWNS -> Reliance Retail
             * "Digital Services business" → Extract: Digital Services (Company), Reliance Industries Limited -> OWNS -> Digital Services
        3. Extract 5 entities and 5 relationships
        4. Extract financial amounts (revenue, profit, assets, debt, equity) - ONLY amounts with currency symbols
        5. Must Extract risk factors as entities (e.g., Market volatility risk, Regulatory compliance risk)
        6. Create relationships with CORRECT directions:
           - Company -> HAS_REVENUE -> Dollar Amount
           - Company -> HAS_PROFIT -> Dollar Amount
           - Person -> MANAGING_DIRECTOR -> Company
           - Person -> FOUNDER -> Company
           - Company -> OWNS -> Company
        6. DO NOT create relationships where:
           - Dollar Amount -> HAS_REVENUE -> Company (WRONG DIRECTION!)
           - Company -> HAS_REVENUE -> Person (WRONG! Person cannot be a financial amount)
           - Company -> HAS_PROFIT -> Person (WRONG! Person cannot be a financial amount)
           - Event -> HAS_REVENUE -> Company (Events cannot have revenue!)
           - Date -> HAS_ASSET -> Location (Dates cannot have assets!)
           - Company -> HAS_REVENUE -> Company (WRONG! Company cannot be a financial amount, use OWNS instead)
        
        REQUIRED JSON FORMAT:
        {{
          "entities": [
            {{
              "id": "name of the entity",
              "type": "Company|Person|Location|Dollar Amount|Risk|Product|Framework|Metric",
              "metadata": "Description or context"
            }}
          ],
          "relationships": [
            {{
              "source": "name of the entity",
              "target": "name of the entity",
              "relation": "OWNS|HAS_PROFIT|CHAIRMAN|FOUNDER|OPERATES|EMPLOYS|LOCATED_IN|FACES_RISK|HAS_REVENUE|HAS_ASSET|HAS_EQUITY|HAS_DEBT"
            }}
          ]
        }}
        
        EXAMPLE - Company Ownership:
        If text says "Reliance Industries Limited owns Jio and Reliance Retail":
        {{
          "entities": [
            {{"id": "Reliance Industries Limited", "type": "Company", "metadata": "Parent company"}},
            {{"id": "Jio", "type": "Company", "metadata": "Subsidiary"}},
            {{"id": "Reliance Retail", "type": "Company", "metadata": "Subsidiary"}}
          ],
          "relationships": [
            {{"source": "Reliance Industries Limited", "target": "Jio", "relation": "OWNS"}},
            {{"source": "Reliance Industries Limited", "target": "Reliance Retail", "relation": "OWNS"}}
          ]
        }}
        """

    def _chunk_text(self, text, chunk_size, overlap):
        """Split text into chunks with overlap."""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position forward by chunk_size - overlap
            start += chunk_size - overlap
            
            # Prevent infinite loop
            if start >= text_length:
                break
        
        return chunks
    
    def _normalize_name(self, name):
        """Normalize entity name for comparison - handles variations and abbreviations."""
        if not name:
            return ""
        
        name = str(name).strip()
        normalized = name.lower()
        
        # Remove common person name prefixes and titles
        person_titles = ["shri", "shri.", "shree", "mr.", "mr", "mrs.", "mrs", "ms.", "ms", 
                        "dr.", "dr", "prof.", "prof", "sir", "madam", "smt.", "smt"]
        for title in person_titles:
            # Remove title at the begiremove the nning
            if normalized.startswith(title + " "):
                normalized = normalized[len(title):].strip()
            if normalized.startswith(title + "."):
                normalized = normalized[len(title) + 1:].strip()
        
        # Remove common company suffixes and prefixes
        normalized = normalized.replace(" limited", "").replace(" ltd", "").replace(" ltd.", "")
        normalized = normalized.replace(" industries", "").replace(" industry", "")
        normalized = normalized.replace(" corporation", "").replace(" corp", "").replace(" corp.", "")
        normalized = normalized.replace(" incorporated", "").replace(" inc", "").replace(" inc.", "")
        
        # Remove punctuation for better matching
        normalized = normalized.replace(".", "").replace(",", "").replace("-", " ").replace("_", " ")
        
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        
        return normalized
    
    def _is_same_entity(self, name1, name2):
        """Check if two entity names refer to the same entity."""
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Exact match
        if norm1 == norm2:
            return True
        
        # For person names, check if core name matches (ignoring middle initials)
        # e.g., "mukesh d ambani" vs "mukesh ambani" vs "shri mukesh d ambani"
        words1 = norm1.split()
        words2 = norm2.split()
        
        # Remove single-letter words (likely middle initials like "d", "h")
        core_words1 = [w for w in words1 if len(w) > 1]
        core_words2 = [w for w in words2 if len(w) > 1]
        
        # If core words match (ignoring order), likely same person
        if len(core_words1) >= 2 and len(core_words2) >= 2:
            if set(core_words1) == set(core_words2):
                return True
            # Check if all core words from shorter name are in longer name
            if len(core_words1) <= len(core_words2):
                if all(word in core_words2 for word in core_words1):
                    return True
            else:
                if all(word in core_words1 for word in core_words2):
                    return True
        
        # Check if one is abbreviation of the other (for companies)
        words1_set = set(norm1.split())
        words2_set = set(norm2.split())
        
        # If one name is subset of another (e.g., "ril" in "reliance industries limited")
        if words1_set and words2_set:
            if words1_set.issubset(words2_set) or words2_set.issubset(words1_set):
                return True
        
        # Check for common abbreviations (e.g., "RIL" = "Reliance Industries Limited")
        if len(norm1) <= 5 and norm1 in norm2:
            return True
        if len(norm2) <= 5 and norm2 in norm1:
            return True
        
        return False
    
    def _deduplicate_entities(self, entities):
        """Remove duplicate entities, keeping the one with best metadata."""
        entity_map = {}
        
        for entity in entities:
            if not isinstance(entity, dict):
                continue
            
            entity_id = entity.get('id') or entity.get('name') or ''
            if not entity_id:
                continue
            
            # Check if this entity already exists (exact or similar)
            found_duplicate = False
            for existing_id, existing_entity in entity_map.items():
                if self._is_same_entity(entity_id, existing_id):
                    found_duplicate = True
                    # Keep the one with better metadata or longer name (more complete)
                    existing_metadata = str(existing_entity.get('metadata', '') or '')
                    new_metadata = str(entity.get('metadata', '') or '')
                    existing_name_len = len(str(existing_id))
                    new_name_len = len(str(entity_id))
                    
                    # Prefer longer name (more complete) or better metadata
                    if (new_name_len > existing_name_len) or (len(new_metadata) > len(existing_metadata) and new_metadata):
                        entity_map[existing_id] = entity
                        # Update key if name is more complete
                        if new_name_len > existing_name_len:
                            del entity_map[existing_id]
                            entity_map[entity_id] = entity
                    break
            
            if not found_duplicate:
                entity_map[entity_id] = entity
        
        return list(entity_map.values())
    
    def _deduplicate_relationships(self, relationships, entity_map=None):
        """Remove duplicate relationships, using entity normalization."""
        if entity_map is None:
            entity_map = {}
        
        # Create mapping: normalized_name -> canonical_name (best version)
        normalized_to_canonical = {}
        for orig_name in entity_map.keys():
            norm = self._normalize_name(orig_name)
            # Use the longest/most complete name as canonical
            if norm not in normalized_to_canonical:
                normalized_to_canonical[norm] = orig_name
            elif len(orig_name) > len(normalized_to_canonical[norm]):
                normalized_to_canonical[norm] = orig_name
        
        relationship_set = set()
        unique_relationships = []
        
        for rel in relationships:
            if not isinstance(rel, dict):
                continue
            
            source = rel.get('source') or rel.get('entity1') or rel.get('from') or ''
            target = rel.get('target') or rel.get('entity2') or rel.get('to') or ''
            relation = rel.get('relation') or rel.get('type') or rel.get('relationship') or 'RELATED_TO'
            
            if not source or not target:
                continue
            
            # Normalize source and target names
            normalized_source = self._normalize_name(source)
            normalized_target = self._normalize_name(target)
            normalized_relation = relation.strip().upper()
            
            # Find canonical names by checking if source/target match any entity
            canonical_source = source
            canonical_target = target
            
            # Check if source matches any existing entity (using _is_same_entity for fuzzy matching)
            for orig_name in entity_map.keys():
                if self._is_same_entity(source, orig_name):
                    norm = self._normalize_name(orig_name)
                    canonical_source = normalized_to_canonical.get(norm, orig_name)
                    normalized_source = norm
                    break
            
            # Check if target matches any existing entity
            for orig_name in entity_map.keys():
                if self._is_same_entity(target, orig_name):
                    norm = self._normalize_name(orig_name)
                    canonical_target = normalized_to_canonical.get(norm, orig_name)
                    normalized_target = norm
                    break
            
            # Also check relationships against each other for duplicates
            # (e.g., "Shri Dhirubhai Ambani" vs "Shri. Dhirubhai H. Ambani")
            is_duplicate = False
            for existing_rel in unique_relationships:
                existing_source = existing_rel.get('source') or existing_rel.get('entity1') or existing_rel.get('from') or ''
                existing_target = existing_rel.get('target') or existing_rel.get('entity2') or existing_rel.get('to') or ''
                existing_relation = existing_rel.get('relation') or existing_rel.get('type') or existing_rel.get('relationship') or ''
                
                if (normalized_relation == existing_relation.strip().upper() and
                    self._is_same_entity(source, existing_source) and
                    self._is_same_entity(target, existing_target)):
                    is_duplicate = True
                    # Keep the one with more complete names (longer)
                    if (len(source) > len(existing_source) or len(target) > len(existing_target)):
                        # Replace the existing one
                        unique_relationships.remove(existing_rel)
                        relationship_set.discard((self._normalize_name(existing_source), 
                                                 self._normalize_name(existing_target), 
                                                 normalized_relation))
                        is_duplicate = False  # Allow adding the better version
                    break
            
            if not is_duplicate:
                rel_key = (normalized_source, normalized_target, normalized_relation)
                if rel_key not in relationship_set:
                    relationship_set.add(rel_key)
                    # Use canonical names in the relationship
                    rel_copy = rel.copy()
                    rel_copy['source'] = canonical_source
                    rel_copy['target'] = canonical_target
                    unique_relationships.append(rel_copy)
        
        return unique_relationships

    def analyze(self, raw_text):
        """
        Analyze text by chunking it if too long, then merge results.
        """
        # Determine if we need to chunk
        max_text_length = 10000  # Maximum characters to send at once
        chunk_size = Config.CHUNK_SIZE
        overlap = Config.CHUNK_OVERLAP
        
        # If text is short enough, process entire text directly
        if len(raw_text) <= max_text_length:
            logger.info(f"Text length ({len(raw_text)} chars) is manageable, processing directly")
            return self._process_single_chunk(raw_text)
        
        # Text is too long, need to chunk the text to small chunks
        logger.info(f"Text length ({len(raw_text)} chars) exceeds limit ({max_text_length}), chunking...")
        chunks = self._chunk_text(raw_text, chunk_size, overlap)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        # The graph to store the entities and relationships
        final_graph = {"entities": [], "relationships": []}
        
        # Process each chunk with incremental deduplication to avoid duplicates of the entities and relationships already extracted
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i + 1}/{len(chunks)} ({len(chunk)} chars)...")
            
            # Retry logic for each chunk
            for attempt in range(2):
                try:
                    # Get already extracted entities to avoid duplicates of the entities already extracted
                    existing_entity_names = {self._normalize_name(e.get('id') or e.get('name') or '') 
                                           for e in final_graph["entities"] if isinstance(e, dict)}
                    
                    chunk_result = self._process_single_chunk(chunk, existing_entities=existing_entity_names)
                    
                    # Merge results
                    if "entities" in chunk_result:
                        final_graph["entities"].extend(chunk_result["entities"])
                    if "relationships" in chunk_result:
                        final_graph["relationships"].extend(chunk_result["relationships"])
                    
                    # Incremental deduplication after each chunk
                    final_graph["entities"] = self._deduplicate_entities(final_graph["entities"])
                    # Create entity map for relationship deduplication
                    entity_map = {}
                    for e in final_graph["entities"]:
                        if isinstance(e, dict):
                            entity_id = e.get('id') or e.get('name') or ''
                            if entity_id:
                                entity_map[entity_id] = e
                    final_graph["relationships"] = self._deduplicate_relationships(final_graph["relationships"], entity_map)
                    
                    logger.info(f"Chunk {i + 1} success: +{len(chunk_result.get('entities', []))} entities, +{len(chunk_result.get('relationships', []))} relationships")
                    logger.info(f"After dedup: {len(final_graph['entities'])} unique entities, {len(final_graph['relationships'])} unique relationships")
                    break  # Success, move to next chunk
                    
                except json.JSONDecodeError as e:
                    if attempt < 1:
                        logger.warning(f"Chunk {i + 1} JSON parse failed (attempt {attempt+1}), retrying...")
                        time.sleep(1)
                    else:
                        logger.error(f"Chunk {i + 1} JSON parse failed after 2 attempts, skipping chunk")
                        break
                except Exception as e:
                    if attempt < 1:
                        logger.warning(f"Chunk {i + 1} error (attempt {attempt+1}): {e}, retrying...")
                        time.sleep(1)
                    else:
                        logger.error(f"Chunk {i + 1} error after 2 attempts: {e}, skipping chunk")
                        break
        
        # Final deduplication pass (in case incremental dedup missed anything)
        logger.info(f"Final deduplication pass: {len(final_graph['entities'])} entities, {len(final_graph['relationships'])} relationships")
        
        # Filter out invalid entity types (dates, events, documents that shouldn't be in financial graph)
        final_graph['entities'] = self._filter_invalid_entities(final_graph['entities'])
        
        final_graph['entities'] = self._deduplicate_entities(final_graph['entities'])
        # Create entity map for relationship deduplication
        entity_map = {}
        for e in final_graph['entities']:
            if isinstance(e, dict):
                entity_id = e.get('id') or e.get('name') or ''
                if entity_id:
                    entity_map[entity_id] = e
        final_graph['relationships'] = self._deduplicate_relationships(final_graph['relationships'], entity_map)
        
        # Validate and fix relationship directions
        final_graph['relationships'] = self._validate_and_fix_relationships(final_graph['relationships'], entity_map)
        
        logger.info(f"Final result: {len(final_graph['entities'])} unique entities, {len(final_graph['relationships'])} unique relationships")
        
        return final_graph
    
    def _filter_invalid_entities(self, entities):
        """Filter out entities that shouldn't be in a financial knowledge graph."""
        invalid_types = ['Date', 'Event', 'Document']  # These are usually not useful entities
        valid_entities = []
        removed_count = 0
        
        # Date patterns to detect
        date_patterns = ['fy ', 'cy', 'march', 'april', 'may', 'june', 'july', 'august', 
                        'september', 'october', 'november', 'december', 'january', 'february']
        year_patterns = ['2024', '2025', '2026', '2023', '2022']
        
        for entity in entities:
            if not isinstance(entity, dict):
                continue
            
            entity_type = entity.get('type', 'default')
            entity_id = str(entity.get('id') or entity.get('name') or '').lower()
            
            # Check if it's a date pattern
            is_date = False
            if any(pattern in entity_id for pattern in date_patterns):
                is_date = True
            elif any(year in entity_id for year in year_patterns) and len(entity_id) < 20:
                # Short strings with years are likely dates
                is_date = True
            
            if is_date:
                logger.debug(f"Filtering out date entity: {entity.get('id') or entity.get('name')}")
                removed_count += 1
                continue
            
            # Filter invalid types
            if entity_type in invalid_types:
                logger.debug(f"Filtering out {entity_type} entity: {entity.get('id') or entity.get('name')}")
                removed_count += 1
                continue
            
            # Filter percentages classified as Dollar Amount
            if entity_type == 'Dollar Amount':
                entity_id_str = str(entity.get('id') or entity.get('name') or '')
                if '%' in entity_id_str and len(entity_id_str) < 10:
                    logger.debug(f"Filtering out percentage misclassified as Dollar Amount: {entity_id_str}")
                    removed_count += 1
                    continue
            
            valid_entities.append(entity)
        
        if removed_count > 0:
            logger.info(f"Filtered out {removed_count} invalid entities (dates, events, documents, percentages)")
        
        return valid_entities
    
    def _validate_and_fix_relationships(self, relationships, entity_map):
        """
        Validate relationships and fix incorrect directions.
        - Fix reversed financial relationships (Dollar Amount -> HAS_REVENUE -> Company should be Company -> HAS_REVENUE -> Dollar Amount)
        - Remove invalid relationships (Events/Dates having financial relationships)
        """
        financial_relations = ['HAS_REVENUE', 'HAS_PROFIT', 'HAS_ASSET', 'HAS_EQUITY', 'HAS_DEBT', 'HAS_EXPORTS', 'HAS_CSR_CONTRIBUTION']
        invalid_source_types = ['Event', 'Date', 'Document', 'Metric']  # These cannot have financial relationships
        
        valid_relationships = []
        fixed_count = 0
        removed_count = 0
        
        for rel in relationships:
            if not isinstance(rel, dict):
                continue
            
            source = rel.get('source') or rel.get('entity1') or rel.get('from') or ''
            target = rel.get('target') or rel.get('entity2') or rel.get('to') or ''
            relation = rel.get('relation') or rel.get('type') or rel.get('relationship') or 'RELATED_TO'
            
            if not source or not target:
                removed_count += 1
                continue
            
            # Get entity types
            source_entity = entity_map.get(source, {})
            target_entity = entity_map.get(target, {})
            source_type = source_entity.get('type', 'default') if isinstance(source_entity, dict) else 'default'
            target_type = target_entity.get('type', 'default') if isinstance(target_entity, dict) else 'default'
            
            relation_upper = relation.strip().upper()
            
            # Check if financial relationship is reversed
            if relation_upper in financial_relations:
                # Financial relationships should be: Company -> relation -> Dollar Amount
                # NEVER: Company -> HAS_REVENUE -> Person (WRONG!)
                # NEVER: Company -> HAS_PROFIT -> Person (WRONG!)
                
                # Check for invalid target types (Person, Company, etc. cannot be financial amounts)
                invalid_target_types = ['Person', 'Company', 'Event', 'Date', 'Document', 'Location', 'Risk', 'Product', 'Framework']
                if target_type in invalid_target_types:
                    logger.warning(f"Removing invalid financial relationship: {source} ({source_type}) -> {relation} -> {target} ({target_type}) (target must be Dollar Amount or Metric, not {target_type})")
                    removed_count += 1
                    continue
                
                # If reversed, fix it
                if target_type == 'Company' and source_type == 'Dollar Amount':
                    # Reversed! Fix it
                    logger.warning(f"Fixing reversed relationship: {source} -> {relation} -> {target} (should be {target} -> {relation} -> {source})")
                    rel['source'] = target
                    rel['target'] = source
                    fixed_count += 1
                elif source_type in invalid_source_types:
                    # Invalid: Event/Date cannot have financial relationships
                    logger.warning(f"Removing invalid relationship: {source} ({source_type}) -> {relation} -> {target}")
                    removed_count += 1
                    continue
                elif source_type != 'Company':
                    # Source should be a Company for financial relationships
                    logger.warning(f"Removing invalid relationship: {source} ({source_type}) -> {relation} -> {target} (source must be Company)")
                    removed_count += 1
                    continue
            
            # Check for other invalid relationships
            if relation_upper in ['FACES_RISK'] and source_type != 'Company':
                logger.warning(f"Removing invalid relationship: {source} ({source_type}) -> {relation} -> {target} (only Companies can face risks)")
                removed_count += 1
                continue
            
            if relation_upper in ['OWNS']:
                # OWNS relationships must be: Company -> OWNS -> Company
                if source_type != 'Company':
                    logger.warning(f"Removing invalid OWNS relationship: {source} ({source_type}) -> OWNS -> {target} (only Companies can own)")
                    removed_count += 1
                    continue
                elif target_type != 'Company':
                    logger.warning(f"Removing invalid OWNS relationship: {source} -> OWNS -> {target} ({target_type}) (can only own Companies)")
                    removed_count += 1
                    continue
                else:
                    # Valid OWNS relationship: Company -> OWNS -> Company
                    logger.debug(f"Valid OWNS relationship: {source} -> OWNS -> {target}")
                    valid_relationships.append(rel)
                    continue
            
            valid_relationships.append(rel)
        
        if fixed_count > 0:
            logger.info(f"Fixed {fixed_count} reversed relationships")
        if removed_count > 0:
            logger.info(f"Removed {removed_count} invalid relationships")
        
        return valid_relationships
    
    def _process_single_chunk(self, chunk_text, existing_entities=None):
        """Process a single chunk of text."""
        prompt = self.get_extraction_prompt(existing_entities=existing_entities)
        raw_response = self.llm.generate_extraction(prompt, chunk_text)
        
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
            return {"entities": [], "relationships": []}
