#!/bin/sh
# Vygeneruje letáky a PDF pro RH030–RH060 (viz gen.py)
cd "$(dirname "$0")" && python3 gen.py
