"""Sdílené pomocné funkce pro rebrand prezentace RHX20 Pro / RHX30 Pro (python-pptx + lxml).
Práce s odstavci je stejná jako u prezentace RH06–RH16 (../prezentace/common.py)."""
import os
import re
import sys

import importlib.util
_spec = importlib.util.spec_from_file_location(
    'common_rh', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'prezentace', 'common.py'))
_rh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rh)
fmt_key, iter_paragraphs, runs, para_text = _rh.fmt_key, _rh.iter_paragraphs, _rh.runs, _rh.para_text
groups, text_groups, to_tagged = _rh.groups, _rh.text_groups, _rh.to_tagged
from pptx import Presentation  # noqa: F401
from pptx.oxml.ns import qn  # noqa: F401

DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DIR, '..', '..', 'R290 Cleanlife Ultra- Light Commercial HP Introduction 20kw 30kw.pptx')
PREV = os.path.join(DIR, '..', 'prezentace')               # upravené obrázky šablony z prezentace RH06–RH16
REBUILT = set()


def rename_models(t):
    """Typová označení výrobce → REO HEATING."""
    big = {'20': 'RHX20 Pro', '30': 'RHX30 Pro'}
    t = re.sub(r'PW(\d{2})-DKXLRE\d-H8', lambda m: big.get(m.group(1), 'RH' + m.group(1) + ' 3F'), t)
    t = re.sub(r'PW20/30\s*KW', 'RHX20 Pro / RHX30 Pro', t, flags=re.I)
    t = re.sub(r'PW06/08/10/12/14/16\s*KW', 'RH06–RH16', t, flags=re.I)
    t = re.sub(r'\bPW(\d{2})\b', lambda m: big.get(m.group(1), 'RH' + m.group(1)), t)
    t = re.sub(r'Power\s*World', 'REO HEATING', t, flags=re.I)
    t = re.sub(r'(Helios|Cleanlife)(\s*(Ultra|Pro))?', 'REO R290 Smart', t, flags=re.I)
    return t
