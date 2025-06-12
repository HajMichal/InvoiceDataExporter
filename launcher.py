#!/usr/bin/env python3
"""
Main launcher for the Invoice Reader application
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui import ModernPDFProcessor

if __name__ == "__main__":
    app = ModernPDFProcessor()
    app.run()