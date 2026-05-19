#!/usr/bin/env python3
"""
Tests for ingest pipeline
Run with: python .processing/scripts/test_ingest.py
"""

import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".processing" / "scripts"))

# Import the module
import importlib.util
spec = importlib.util.spec_from_file_location("ingest_module", PROJECT_ROOT / ".processing" / "scripts" / "ingest.py")
ingest_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingest_module)


class TestTransliteration(unittest.TestCase):
    """Test name transliteration."""

    def test_simple_name(self):
        """Test simple First Last name."""
        result = ingest_module.transliterate_name_to_pinyin("John Smith")
        self.assertIsNotNone(result)

    def test_last_first_name(self):
        """Test Last, First format."""
        result = ingest_module.transliterate_name_to_pinyin("Smith, John")
        self.assertIsNotNone(result)

    def test_name_with_suffix(self):
        """Test name with Jr/Sr suffix."""
        result = ingest_module.transliterate_name_to_pinyin("Austin, A. Everett, Jr.")
        self.assertIsNotNone(result)
        self.assertIn("奥斯汀", result)

    def test_name_with_initial(self):
        """Test name with initial."""
        result = ingest_module.transliterate_name_to_pinyin("A. Everett Austin")
        self.assertIsNotNone(result)


class TestChicagoBibliography(unittest.TestCase):
    """Test bibliography formatting."""

    def test_format_bibliography_item(self):
        """Test single bibliography item formatting."""
        entry = {"text": "Author. Title of work. Publisher, 2020.", "year": "2020"}
        result = ingest_module.format_bibliography_item(entry)
        self.assertIsNotNone(result)

    def test_parse_chicago_entry(self):
        """Test Chicago entry parsing."""
        text = "Smith, John. *The Art of History*. New York: Publisher, 2020."
        result = ingest_module.parse_chicago_entry(text)
        self.assertIsNotNone(result)


class TestUtilities(unittest.TestCase):
    """Test utility functions."""

    def test_strip_html(self):
        """Test HTML stripping."""
        html = "<p>Hello <b>World</b></p>"
        result = ingest_module.strip_html(html)
        self.assertEqual(result, "Hello World")

    def test_has_chinese_chars(self):
        """Test Chinese character detection."""
        self.assertTrue(ingest_module.has_chinese_chars("奥斯汀"))
        self.assertFalse(ingest_module.has_chinese_chars("Austin"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
