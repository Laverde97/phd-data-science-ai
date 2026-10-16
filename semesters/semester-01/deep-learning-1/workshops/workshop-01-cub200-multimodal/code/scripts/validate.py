#!/usr/bin/env python3
"""Ejecuta smoke tests de ambos frameworks con muestras reales."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from cub200.common import load_artifacts, set_seeds
from cub200.quality import audit_prepared, check_batch

p=argparse.ArgumentParser()
p.add_argument('--data-dir',default='data')
p.add_argument('--artifacts-dir',default='artifacts')
p.add_argument('--framework',choices=['torch','tf','both'],default='both')
p.add_argument('--batch-size',type=int,default=16)
a=p.parse_args()
set_seeds()
m,f,t,l,metadata=load_artifacts(a.artifacts_dir,a.data_dir)
audit_prepared(m,f,t,l,metadata)
print('Auditoría compartida: OK')
if a.framework in ('torch','both'):
    from cub200.pytorch_pipeline import make_torch_loaders
    datasets=make_torch_loaders(m,f,t,l,batch_size=a.batch_size)
    for split, loader in datasets.items():
        result=check_batch(next(iter(loader)),framework='torch',max_len=metadata['max_len'])
        print('PyTorch',split,result)
if a.framework in ('tf','both'):
    from cub200.tensorflow_pipeline import make_tf_datasets
    datasets=make_tf_datasets(m,f,t,l,batch_size=a.batch_size)
    for split, ds in datasets.items():
        result=check_batch(next(iter(ds)),framework='tf',max_len=metadata['max_len'])
        print('TensorFlow',split,result)
print('Contrato multimodal: OK')
