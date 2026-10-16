"""Funciones de procesamiento compartidas por PyTorch y TensorFlow."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import json
import math
import random
import re

import numpy as np
from PIL import Image

SEED = 42
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)
ATTR_COUNT = 312
CLASS_COUNT = 200
EXPECTED_COUNTS = {'train': 5394, 'val': 600, 'test': 5794}


def set_seeds(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except ImportError:
        pass


def tokenize(text: str) -> list[str]:
    """Según consigna: minúsculas, letras inglesas, sin puntuación ni números."""
    return re.findall(r'[a-z]+', text.lower())


def load_captions(path: Path) -> list[str]:
    lines = [s.strip() for s in Path(path).read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    if len(lines) != 10:
        raise ValueError(f'Se esperaban 10 captions, se encontraron {len(lines)}: {path}')
    return lines


def fit_text(train_captions: list[str]) -> tuple[dict[str, int], int]:
    """Construye el vocabulario y percentil 95 exclusivamente con las captions de train."""
    counts = Counter(word for caption in train_captions for word in tokenize(caption))
    vocab = {'<pad>': 0, '<unk>': 1}
    for word, frequency in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        if frequency >= 2:
            vocab[word] = len(vocab)
    lengths = [len(tokenize(s)) for s in train_captions]
    if not lengths:
        raise ValueError('No hay captions de train para ajustar el vocabulario')
    max_len = max(1, int(math.ceil(np.percentile(lengths, 95))))
    return vocab, max_len


def encode_caption(text: str, vocab: dict[str, int], max_len: int):
    ids = [vocab.get(word, 1) for word in tokenize(text)][:max_len]
    if not ids:
        ids = [1]
    length = min(max(1, len(ids)), max_len)
    padded = np.zeros(max_len, dtype=np.int32)
    padded[:length] = ids[:length]
    return padded, np.int32(length)


def clip_bbox_to_image(x, y, w, h, W, H):
    """Intersección bbox-imagen; rechaza datos inválidos o sin solapamiento.

    Conserva la anotación original en la fuente; el clipping solo se usa
    para características geométricas calculadas a partir de píxeles visibles.
    """
    values = tuple(map(float, (x, y, w, h, W, H)))
    x, y, w, h, W, H = values
    if not all(math.isfinite(v) for v in values):
        raise ValueError(f'Bounding box no finita: {values}')
    if w <= 0 or h <= 0 or W <= 0 or H <= 0:
        raise ValueError(f'Bounding box o imagen con tamaño no positivo: {values}')

    x0, y0 = max(0.0, x), max(0.0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f'Bounding box sin intersección con imagen: {values}')
    return (x0, y0, x1 - x0, y1 - y0)


def bbox_geometry(x, y, w, h, W, H) -> np.ndarray:
    """6 geometrías de la porción visible; bordes anotados se recortan al lienzo."""
    x, y, w, h = clip_bbox_to_image(x, y, w, h, W, H)
    W, H = float(W), float(H)
    return np.asarray(((x + w / 2) / W, (y + h / 2) / H,
                       w / W, h / H, w / h, (w * h) / (W * H)), dtype=np.float32)


def crop_bbox_pil(image: Image.Image, bbox, margin: float = .10) -> Image.Image:
    W, H = image.size
    x, y, w, h = map(float, bbox)
    left = max(0, int(math.floor(x - margin*w)))
    top = max(0, int(math.floor(y - margin*h)))
    right = min(W, int(math.ceil(x + w + margin*w)))
    bottom = min(H, int(math.ceil(y + h + margin*h)))
    if right <= left or bottom <= top:
        raise ValueError('Recorte vacío; revise las anotaciones de bounding box')
    return image.crop((left, top, right, bottom))


def load_artifacts(artifacts_dir, data_dir):
    """Resuelve rutas de imágenes/captions sin guardar rutas absolutas no portables."""
    import pandas as pd
    p = Path(artifacts_dir)
    data_dir = Path(data_dir)
    manifest = pd.read_csv(p / 'manifest.csv').sort_values('image_id').reset_index(drop=True)
    manifest['image_path'] = manifest['relpath'].map(lambda x: str(data_dir / 'CUB_200_2011' / 'images' / x))
    manifest['caption_path'] = manifest['relpath'].map(lambda x: str(data_dir / 'text_c10' / Path(x).with_suffix('.txt')))
    features = np.load(p / 'tabular.npy')
    text_ids = np.load(p / 'text_ids.npy')
    lengths = np.load(p / 'text_lengths.npy')
    metadata = json.loads((p / 'metadata.json').read_text(encoding='utf-8'))
    assert manifest.image_id.is_unique, 'IDs duplicados en manifest'
    assert len(manifest) == len(features) == len(text_ids) == len(lengths)
    assert features.shape[1] == 318 and text_ids.shape[1] == 10
    if manifest['image_path'].map(lambda s: not Path(s).is_file()).any():
        raise FileNotFoundError('Faltan imágenes. Revise --data-dir y la extracción del archivo original.')
    return manifest, features, text_ids, lengths, metadata
