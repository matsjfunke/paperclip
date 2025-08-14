#!/usr/bin/env python3
"""
Unit tests for metadata retrieval functionality.
"""

import unittest
import sys
import os

# Add src to path to import server modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import (
    fetch_single_arxiv_paper_metadata,
    fetch_single_openalex_paper_metadata,
    fetch_single_osf_preprint_metadata,
)


class TestMetadataRetrieval(unittest.TestCase):
    """Test class for paper metadata retrieval."""

    def setUp(self):
        """Set up test fixtures."""
        self.osf_id = "2stpg"
        self.openalex_id = "W4385245566" 
        self.arxiv_id = "1709.06308v1"
        
        # Expected results based on tmp.py output
        self.expected_osf_title = "The Economy of Attention and the Novel"
        self.expected_openalex_title = "Attention Is All You Need"
        self.expected_arxiv_title = "Exploring Human-like Attention Supervision in Visual Question Answering"

    def test_osf_metadata_retrieval(self):
        """Test OSF paper metadata retrieval."""
        result = fetch_single_osf_preprint_metadata(self.osf_id)
        
        # Assert that result is a dictionary and not an error
        self.assertIsInstance(result, dict)
        self.assertNotIn("status", result) or result.get("status") != "error"
        
        # Assert title and ID
        self.assertEqual(result.get("title"), self.expected_osf_title)
        self.assertEqual(result.get("id"), self.osf_id)

    def test_openalex_metadata_retrieval(self):
        """Test OpenAlex paper metadata retrieval.""" 
        result = fetch_single_openalex_paper_metadata(self.openalex_id)
        
        # Assert that result is a dictionary and not an error
        self.assertIsInstance(result, dict)
        self.assertNotIn("status", result) or result.get("status") != "error"
        
        # Assert title and ID
        self.assertEqual(result.get("title"), self.expected_openalex_title)
        self.assertEqual(result.get("id"), self.openalex_id)

    def test_arxiv_metadata_retrieval(self):
        """Test ArXiv paper metadata retrieval."""
        result = fetch_single_arxiv_paper_metadata(self.arxiv_id)
        
        # Assert that result is a dictionary and not an error
        self.assertIsInstance(result, dict)
        self.assertNotIn("status", result) or result.get("status") != "error"
        
        # Assert title and ID
        self.assertEqual(result.get("title"), self.expected_arxiv_title)
        self.assertEqual(result.get("id"), self.arxiv_id)

    def test_metadata_contains_required_fields(self):
        """Test that metadata contains essential fields."""
        result = fetch_single_arxiv_paper_metadata(self.arxiv_id)
        
        # Assert required fields are present
        self.assertIn("title", result)
        self.assertIn("id", result)
        self.assertIsNotNone(result.get("title"))
        self.assertIsNotNone(result.get("id"))


if __name__ == "__main__":
    unittest.main()