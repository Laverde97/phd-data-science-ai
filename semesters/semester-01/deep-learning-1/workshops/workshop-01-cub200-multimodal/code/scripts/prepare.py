#!/usr/bin/env python3
"""Desde la raíz: python scripts/prepare.py --data-dir data --artifacts-dir artifacts"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from cub200.prepare import prepare

p=argparse.ArgumentParser(description='Prepara CUB-200-2011 + captions, sin entrenar modelos')
p.add_argument('--data-dir',default='data')
p.add_argument('--artifacts-dir',default='artifacts')
a=p.parse_args()
prepare(a.data_dir,a.artifacts_dir)
