#!/usr/bin/env python3
"""Launch the TTRPG Convert Content Selector GUI."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from gui.content_selector import main

if __name__ == "__main__":
    raise SystemExit(main())
