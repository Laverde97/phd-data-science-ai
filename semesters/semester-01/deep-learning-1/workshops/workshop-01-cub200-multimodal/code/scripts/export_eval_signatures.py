#!/usr/bin/env python3
"""Exporta la parte determinista de batches de val/test en un framework.

Ejecutar con el intérprete de PyTorch o TensorFlow por separado.
Los tensores de imagen se verifican pero no se comparan píxel a píxel.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cub200.common import load_artifacts, set_seeds
from cub200.quality import audit_prepared, check_batch

FIELDS = ('image_id', 'label', 'input_ids', 'lengths', 'tabular')


def to_numpy(x):
    if hasattr(x, 'detach'):
        return x.detach().cpu().numpy()
    if hasattr(x, 'numpy'):
        return x.numpy()
    return np.asarray(x)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--framework', choices=('torch', 'tf'), required=True)
    p.add_argument('--data-dir', default='data')
    p.add_argument('--artifacts-dir', default='artifacts')
    p.add_argument('--output-dir', default='artifacts/reports/signatures')
    p.add_argument('--batch-size', type=int, default=16)
    p.add_argument('--max-batches', type=int, default=2,
                   help='0 = evaluar el split completo; 2 = prueba rápida')
    args = p.parse_args()
    if args.batch_size < 1 or args.max_batches < 0:
        p.error('--batch-size debe ser positivo y --max-batches no negativo')
    set_seeds()
    manifest, features, ids, lengths, metadata = load_artifacts(args.artifacts_dir, args.data_dir)
    audit_prepared(manifest, features, ids, lengths, metadata)

    if args.framework == 'torch':
        from cub200.pytorch_pipeline import make_torch_loaders
        datasets = make_torch_loaders(manifest, features, ids, lengths,
                                      batch_size=args.batch_size, num_workers=0)
    else:
        from cub200.tensorflow_pipeline import make_tf_datasets
        datasets = make_tf_datasets(manifest, features, ids, lengths,
                                    batch_size=args.batch_size)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for split in ('val', 'test'):
        captured = {k: [] for k in FIELDS}
        n_batches = 0
        for batch in datasets[split]:
            check_batch(batch, framework=args.framework, max_len=int(metadata['max_len']))
            for key in FIELDS:
                captured[key].append(to_numpy(batch[key]))
            n_batches += 1
            if args.max_batches and n_batches >= args.max_batches:
                break
        if not n_batches:
            raise RuntimeError(f'Split vacío: {split}')
        merged = {key: np.concatenate(values, axis=0) for key, values in captured.items()}
        # Verificar orden y alineación contra el manifest, además del batch.
        expected = manifest.loc[manifest.split == split, 'image_id'].to_numpy()
        n = len(merged['image_id'])
        np.testing.assert_array_equal(merged['image_id'], expected[:n])
        if args.max_batches == 0:
            assert n == len(expected), f'Split {split}: {n} != {len(expected)}'
        out = output_dir / f'{args.framework}_{split}.npz'
        np.savez_compressed(out, **merged)
        print(f'{args.framework.upper()} {split}: {n}/{len(expected)} observaciones; '
              f'{n_batches} lotes; salida: {out}')
    print('EXPORTACIÓN DE FIRMAS: OK')


if __name__ == '__main__':
    main()
