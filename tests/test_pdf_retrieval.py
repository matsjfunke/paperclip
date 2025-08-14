#!/usr/bin/env python3
"""
Unit tests for PDF retrieval functionality.
"""

import unittest
import sys
import os
import asyncio

# Add src to path to import server modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import (
    fetch_single_arxiv_paper_metadata,
    fetch_single_openalex_paper_metadata,
    fetch_single_osf_preprint_metadata,
)
from utils.pdf2md import download_paper_and_parse_to_markdown


class TestPdfRetrieval(unittest.TestCase):
    """Test class for paper PDF retrieval and content extraction."""

    def setUp(self):
        """Set up test fixtures."""
        self.osf_id = "2stpg"
        self.openalex_id = "W4385245566" 
        self.arxiv_id = "1709.06308v1"
        
        # Expected content starts based on tmp_pdf.py output
        self.expected_osf_start = "#### The Economy of Attention and the Novel"
        self.expected_openalex_start = "Skip to main content"
        self.expected_arxiv_start = "## **Exploring Human-like Attention Supervision in Visual Question Answering**"

    def test_osf_pdf_retrieval(self):
        """Test OSF paper PDF retrieval and content extraction."""
        metadata = fetch_single_osf_preprint_metadata(self.osf_id)
        result = asyncio.run(download_paper_and_parse_to_markdown(
            metadata=metadata,
            pdf_url_field="download_url",
            paper_id=self.osf_id,
            write_images=False
        ))
        
        # Assert that result is successful
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "success")
        
        # Assert content is retrieved and has expected start
        content = result.get("content", "")
        self.assertGreater(len(content), 1000)  # Should have substantial content
        self.assertTrue(content.startswith(self.expected_osf_start))

    def test_openalex_pdf_retrieval(self):
        """Test OpenAlex paper PDF retrieval and content extraction."""
        metadata = fetch_single_openalex_paper_metadata(self.openalex_id)
        result = asyncio.run(download_paper_and_parse_to_markdown(
            metadata=metadata,
            pdf_url_field="pdf_url",
            paper_id=self.openalex_id,
            write_images=False
        ))
        
        # Assert that result is successful
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "success")
        
        # Assert content is retrieved and has expected start
        content = result.get("content", "")
        self.assertGreater(len(content), 1000)  # Should have substantial content
        self.assertTrue(content.startswith(self.expected_openalex_start))

    def test_arxiv_pdf_retrieval(self):
        """Test ArXiv paper PDF retrieval and content extraction."""
        metadata = fetch_single_arxiv_paper_metadata(self.arxiv_id)
        result = asyncio.run(download_paper_and_parse_to_markdown(
            metadata=metadata,
            pdf_url_field="download_url",
            paper_id=self.arxiv_id,
            write_images=False
        ))
        
        # Assert that result is successful
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "success")
        
        # Assert content is retrieved and has expected start
        content = result.get("content", "")
        self.assertGreater(len(content), 1000)  # Should have substantial content
        self.assertTrue(content.startswith(self.expected_arxiv_start))

    def test_pdf_content_contains_markdown(self):
        """Test that PDF content is properly converted to markdown."""
        metadata = fetch_single_arxiv_paper_metadata(self.arxiv_id)
        result = asyncio.run(download_paper_and_parse_to_markdown(
            metadata=metadata,
            pdf_url_field="download_url",
            paper_id=self.arxiv_id,
            write_images=False
        ))
        
        # Assert successful retrieval
        self.assertEqual(result.get("status"), "success")
        
        content = result.get("content", "")
        
        # Assert markdown characteristics are present
        self.assertIn("##", content)  # Should contain markdown headers
        self.assertIn("**", content)  # Should contain bold text
        self.assertGreater(len(content.split('\n')), 50)  # Should have many lines

    def test_pdf_retrieval_includes_metadata(self):
        """Test that PDF retrieval includes paper metadata."""
        metadata = fetch_single_osf_preprint_metadata(self.osf_id)
        result = asyncio.run(download_paper_and_parse_to_markdown(
            metadata=metadata,
            pdf_url_field="download_url",
            paper_id=self.osf_id,
            write_images=False
        ))
        
        # Assert successful retrieval
        self.assertEqual(result.get("status"), "success")
        
        # Assert metadata is included
        result_metadata = result.get("metadata", {})
        self.assertIsInstance(result_metadata, dict)
        self.assertIn("title", result_metadata)
        self.assertIn("id", result_metadata)


if __name__ == "__main__":
    unittest.main()