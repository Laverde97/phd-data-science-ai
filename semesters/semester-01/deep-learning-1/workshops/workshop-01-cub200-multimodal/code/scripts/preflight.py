#!/usr/bin/env python3
"""Comprobación rápida previa a ETL, con un par real imagen-caption."""
from pathlib import Path
import argparse
import pandas as pd
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument('--data-dir',default='data')
args=parser.parse_args()
data=Path(args.data_dir)
cub=data/'CUB_200_2011'
texts=data/'text_c10'
need=[cub/'images.txt',cub/'image_class_labels.txt',cub/'train_test_split.txt',
      cub/'bounding_boxes.txt',cub/'attributes'/'image_attribute_labels.txt',texts]
missing=[str(p) for p in need if not p.exists()]
if missing:
    raise SystemExit('Faltan archivos/carpetas:\n'+'\n'.join(missing))
images=pd.read_csv(cub/'images.txt',sep=r'\s+',header=None,names=['image_id','relpath'])
if len(images)!=11788 or not images.image_id.is_unique:
    raise SystemExit('images.txt no contiene 11.788 imágenes con IDs únicos.')
r=images.iloc[0]
photo=cub/'images'/r.relpath
text=texts/Path(r.relpath).with_suffix('.txt')
if not photo.exists() or not text.exists():
    raise SystemExit(f'No se encontró la pareja de prueba: {photo}\n{text}')
with Image.open(photo) as im:
    im.verify()
lines=[s for s in text.read_text(encoding='utf-8-sig').splitlines() if s.strip()]
if len(lines)!=10:
    raise SystemExit(f'La pareja de prueba requiere 10 captions: {text}')
print('PREFLIGHT OK: 11.788 referencias, fuentes en rutas previstas, imagen de prueba legible, 10 captions.')
print('EJEMPLO:',photo)
