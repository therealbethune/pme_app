#!/usr/bin/env python3
"""
PME App package main entry point.

This allows running the CLI with: python -m pme_app.cli
"""

import sys

from pme_app.cli import main

if __name__ == "__main__":
    sys.exit(main())
