import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
import pytest
from PIL import Image
from cub200.quality import check_batch


def make_small_fixture(tmp_path):
    rows=[]
    for i,split in enumerate(('train','val','test')):
        p=tmp_path/f'{i}.jpg'
        Image.new('RGB',(64,64),(30+i*20,80,50)).save(p)
        rows.append({'image_id':i+1,'image_path':str(p),'split':split,
                     'label':i,'x':5.,'y':5.,'w':45.,'h':40.})
    manifest=pd.DataFrame(rows)
    tab=np.zeros((3,318),dtype=np.float32)
    ids=np.zeros((3,10,7),dtype=np.int32)
    ids[:,:,0]=2
    lengths=np.ones((3,10),dtype=np.int32)
    return manifest,tab,ids,lengths


def test_torch_pipeline(tmp_path):
    pytest.importorskip('torch')
    pytest.importorskip('torchvision')
    from cub200.pytorch_pipeline import make_torch_loaders
    args=make_small_fixture(tmp_path)
    loads=make_torch_loaders(*args,batch_size=2)
    for ds in loads.values():
        check_batch(next(iter(ds)),framework='torch',max_len=7)


def test_tf_pipeline(tmp_path):
    pytest.importorskip('tensorflow')
    from cub200.tensorflow_pipeline import make_tf_datasets
    args=make_small_fixture(tmp_path)
    loads=make_tf_datasets(*args,batch_size=2)
    for ds in loads.values():
        check_batch(next(iter(ds)),framework='tf',max_len=7)
