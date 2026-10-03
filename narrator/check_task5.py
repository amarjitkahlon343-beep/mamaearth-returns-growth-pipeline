#!/usr/bin/env python3
"""Standalone Task 5 checker against narrator/sample_output.txt"""
from pathlib import Path
from generate_narrative import check_narrative

text = Path(__file__).with_name("sample_output.txt").read_text(encoding="utf-8")
raise SystemExit(0 if check_narrative(text) else 1)
