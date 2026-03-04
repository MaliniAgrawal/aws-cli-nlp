#!/usr/bin/env python3
"""
AWS NLP CLI Entry Point
Run from project root: python aws-nlp.py "query"
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the CLI
from src.aws_nlp import main

if __name__ == "__main__":
    main()
