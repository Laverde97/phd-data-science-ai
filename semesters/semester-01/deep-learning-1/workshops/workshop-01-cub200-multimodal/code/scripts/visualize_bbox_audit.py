#!/usr/bin/env python3
"""Genera evidencia visual de las cajas anotadas fuera del límite."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', default='data')
    p.add_argument('--artifacts-dir', default='artifacts')
    p.add_argument('--output', default='artifacts/reports/bbox_top5.png')
    args = p.parse_args()
    audit = pd.read_csv(Path(args.artifacts_dir) / 'bbox_clipping_audit.csv')
    if audit.empty:
        print('Sin cajas recortadas; no se requiere figura.')
        return
    orig = audit.original_w * audit.original_h
    visible = audit.clipped_w * audit.clipped_h
    audit['loss_pct'] = 100 * (1 - visible / orig)
    audit = audit.sort_values('loss_pct', ascending=False)
    cases = audit.head(5)
    fig, axs = plt.subplots(2, 3, figsize=(15, 9), layout='constrained')
    for ax, (_, r) in zip(axs.flat, cases.iterrows()):
        path = Path(args.data_dir) / 'CUB_200_2011' / 'images' / r.relpath
        with Image.open(path) as f:
            image = np.array(f.convert('RGB'))
        h, w = image.shape[:2]
        ax.imshow(image)
        ax.add_patch(Rectangle((r.original_x, r.original_y), r.original_w,
                               r.original_h, fill=False, edgecolor='red', linewidth=2,
                               label='Anotación original'))
        ax.add_patch(Rectangle((r.clipped_x, r.clipped_y), r.clipped_w,
                               r.clipped_h, fill=False, edgecolor='lime', linewidth=1.8,
                               linestyle='--', label='Parte visible'))
        ax.set_xlim(-20, w + 45)
        ax.set_ylim(h + 35, -20)
        ax.set_title(f'ID {r.image_id} · pérdida {r.loss_pct:.2f}%\n{Path(r.relpath).name}',
                     fontsize=9)
        ax.axis('off')
    axs.flat[-1].axis('off')
    handles, labels = axs.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower right')
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'AUDITORÍA VISUAL: {dest} (5 casos de mayor pérdida relativa)')


if __name__ == '__main__':
    main()
