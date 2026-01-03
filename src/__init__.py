"""
Auto path setup - runs automatically when src is import
How it works:
- The __init__.py file makes 'src' a Python package
- When you do 'from src.xxx import yyy', Python automatically runs this file
- __file__ points to this file (src/__init__.py)
- Path(__file__).parent = src/ folder
- Path(__file__).parent.parent = project root
"""
import sys
from pathlib import Path
import os


_project_root = Path(__file__).resolve().parent.parent
_project_root_str = str(_project_root)
_project_root_normalized = os.path.normpath(_project_root_str)

# Normalize all existing paths for comparison (handles Windows/Unix differences)
_normalized_paths = [os.path.normpath(p) for p in sys.path]

# Add to path if not already there (check normalized versions)
if _project_root_normalized not in _normalized_paths:
    sys.path.insert(0, _project_root_str)
