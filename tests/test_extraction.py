import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from unittest.mock import MagicMock
from src.extractor import FinancialDetective

class TestFinancialDetective(unittest.TestCase):
    def test_analyze_structure(self):
        """
        Test if the analyzer correctly parses a valid mocked LLM response.
        """
        mock_response = """
        {
            "entities": [{"id": "RIL", "type": "Company"}],
            "relationships": [{"source": "RIL", "target": "10B", "relation": "REVENUE"}]
        }
        """
        
        detective = FinancialDetective()
        # Mock the LLM engine to avoid actual API calls during testing
        detective.llm.generate_extraction = MagicMock(return_value=mock_response)
        
        result = detective.analyze("Some raw text")
        
        self.assertIn("entities", result)
        self.assertIn("relationships", result)
        self.assertEqual(result["entities"][0]["id"], "RIL")

if __name__ == '__main__':
    unittest.main()