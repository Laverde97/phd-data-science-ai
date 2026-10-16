#!/usr/bin/env python3
"""Compara salidas deterministas PyTorch / TensorFlow sin importar ambos frameworks."""
import argparse
from pathlib import Path
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--signatures-dir', default='artifacts/reports/signatures')
    args = parser.parse_args()
    root = Path(args.signatures_dir)
    for split in ('val', 'test'):
        torch_file = root / f'torch_{split}.npz'
        tf_file = root / f'tf_{split}.npz'
        if not torch_file.exists() or not tf_file.exists():
            parser.error(f'Archivos faltantes: {torch_file} / {tf_file}')
        with np.load(torch_file, allow_pickle=False) as pt, np.load(tf_file, allow_pickle=False) as tf:
            for key in ('image_id', 'label', 'input_ids', 'lengths'):
                np.testing.assert_array_equal(pt[key], tf[key],
                                              err_msg=f'{split}: diferencias en {key}')
            np.testing.assert_allclose(pt['tabular'], tf['tabular'], rtol=0,
                                       atol=1e-6, err_msg=f'{split}: diferencias en tabular')
            n = len(pt['image_id'])
            assert n > 0
            print(f'{split}: {n} observaciones idénticas en IDs, etiquetas y texto; '
                  'atributos tabulares equivalentes (atol=1e-6).')
    print('COMPARACIÓN INTERFRAMEWORK: OK')


if __name__ == '__main__':
    main()
