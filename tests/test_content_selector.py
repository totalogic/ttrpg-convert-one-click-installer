"""Tests for the content selector and source map data."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gui.source_map import (
    OPEN_REFERENCE,
    SOURCES_5E_BOOKS,
    SOURCES_5E_ADVENTURES,
    SOURCES_5E_REFERENCE,
    all_5e_sources,
    source_name_map,
    DEFAULT_CONFIG,
)
from gui.content_selector import ContentSelection


class SourceMapTests(unittest.TestCase):
    def test_open_reference_includes_2024_sources(self):
        ids = [sid for sid, _ in OPEN_REFERENCE]
        self.assertIn("srd52", ids)
        self.assertIn("basicRules2024", ids)

    def test_source_ids_are_unique_per_category(self):
        """Each source ID should appear at most once per category."""
        for sources in (SOURCES_5E_BOOKS, SOURCES_5E_ADVENTURES, SOURCES_5E_REFERENCE):
            ids = [sid for sid, _ in sources]
            self.assertEqual(
                len(ids),
                len(set(ids)),
                f"Duplicate source IDs in {sources}",
            )

    def test_all_5e_sources_returns_tuples(self):
        sources = all_5e_sources()
        self.assertTrue(len(sources) > 50)
        for sid, name, category in sources:
            self.assertIn(category, ("book", "adventure", "reference"))
            self.assertIsInstance(sid, str)
            self.assertIsInstance(name, str)

    def test_source_name_map_covers_all(self):
        m = source_name_map()
        self.assertIn("PHB", m)
        self.assertIn("LMoP", m)
        self.assertIn("srd52", m)

    def test_default_config_has_expected_keys(self):
        self.assertIn("reprintBehavior", DEFAULT_CONFIG)
        self.assertIn("racesAsSpecies", DEFAULT_CONFIG)
        self.assertIn("splitRules", DEFAULT_CONFIG)
        self.assertIn("tagPrefix", DEFAULT_CONFIG)
        self.assertIn("images", DEFAULT_CONFIG)


class ContentSelectionTests(unittest.TestCase):
    def test_default_selection(self):
        sel = ContentSelection()
        self.assertEqual(sel.output_location, "local")
        self.assertEqual(sel.reprint_behavior, "newest")
        self.assertTrue(sel.races_as_species)
        self.assertTrue(sel.split_rules)
        self.assertFalse(sel.use_dice_roller)
        self.assertEqual(sel.tag_prefix, "ttrpg-cli")

    def test_books_dict_initializes_empty(self):
        sel = ContentSelection()
        # After app init, these would be populated; the dataclass itself starts empty
        self.assertEqual(len(sel.books), 0)

    def test_homebrew_files_default_empty(self):
        sel = ContentSelection()
        self.assertEqual(sel.homebrew_files, [])

    def test_config_generation_with_selected_sources(self):
        sel = ContentSelection()
        sel.books["PHB"] = True
        sel.adventures["LMoP"] = True
        sel.reference["srd52"] = True
        sel.homebrew_files.append("/path/to/homebrew.json")

        # Build config manually (mirrors _generate_config logic)
        sources = {}
        selected_books = [sid for sid, val in sel.books.items() if val]
        selected_adventures = [sid for sid, val in sel.adventures.items() if val]
        selected_reference = [sid for sid, val in sel.reference.items() if val]

        if selected_books:
            sources["book"] = selected_books
        if selected_adventures:
            sources["adventure"] = selected_adventures
        if selected_reference:
            sources["reference"] = selected_reference
        if sel.homebrew_files:
            sources["homebrew"] = list(sel.homebrew_files)

        config = {"sources": sources}
        config["reprintBehavior"] = sel.reprint_behavior
        config["racesAsSpecies"] = sel.races_as_species
        config["splitRules"] = sel.split_rules
        config["tagPrefix"] = sel.tag_prefix
        config["images"] = {
            "copyInternal": sel.copy_internal_images,
            "copyExternal": sel.copy_external_images,
        }

        self.assertIn("PHB", config["sources"]["book"])
        self.assertIn("LMoP", config["sources"]["adventure"])
        self.assertIn("srd52", config["sources"]["reference"])
        self.assertIn("/path/to/homebrew.json", config["sources"]["homebrew"])
        self.assertEqual(config["reprintBehavior"], "newest")
        self.assertTrue(config["racesAsSpecies"])

    def test_config_serializes_to_valid_json(self):
        sel = ContentSelection()
        sel.books["PHB"] = True
        sel.reference["srd52"] = True

        sources = {}
        sources["book"] = [sid for sid, val in sel.books.items() if val]
        sources["reference"] = [sid for sid, val in sel.reference.items() if val]

        config = {
            "sources": sources,
            "reprintBehavior": sel.reprint_behavior,
            "racesAsSpecies": sel.races_as_species,
            "splitRules": sel.split_rules,
            "tagPrefix": sel.tag_prefix,
            "images": {
                "copyInternal": sel.copy_internal_images,
                "copyExternal": sel.copy_external_images,
            },
        }

        # Should serialize without errors
        json_str = json.dumps(config, indent=2)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["sources"]["book"], ["PHB"])
        self.assertEqual(parsed["sources"]["reference"], ["srd52"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
