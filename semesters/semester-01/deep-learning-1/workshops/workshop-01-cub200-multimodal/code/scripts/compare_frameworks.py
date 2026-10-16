#!/usr/bin/env python3
"""Compara la parte determinista de val/test entre PyTorch y TensorFlow.

Ignora el contenido exacto del tensor de imagen porque PIL/TF usan kernels distintos.
"""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from cub200.common import load_artifacts,set_seeds
from cub200.pytorch_pipeline import make_torch_loaders
from cub200.tensorflow_pipeline import make_tf_datasets


def main():
    set_seeds()
    m,tab,txt,lens,meta=load_artifacts('artifacts','data')
    a=make_torch_loaders(m,tab,txt,lens,batch_size=16)
    b=make_tf_datasets(m,tab,txt,lens,batch_size=16)
    for split in ('val','test'):
        for torch_batch,tf_batch in zip(a[split],b[split]):
            for key in ('image_id','label','input_ids','lengths','tabular'):
                x=torch_batch[key].detach().cpu().numpy()
                y=tf_batch[key].numpy()
                if key=='tabular':
                    np.testing.assert_allclose(x,y,rtol=0,atol=1e-6)
                else:
                    np.testing.assert_array_equal(x,y)
        print(split,'coincidencia de image_id/labels/text/tabular: OK')

if __name__=='__main__':
    main()
