"""Implementación nativa de PyTorch: map-style Dataset + DataLoader."""
from __future__ import annotations
import random
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from .common import MEAN, STD, SEED, crop_bbox_pil


class CUBMultimodalTorch(Dataset):
    def __init__(self, frame, features, ids, lengths, training=False):
        if not len(frame)==len(features)==len(ids)==len(lengths):
            raise ValueError('El manifest y las matrices deben estar alineados')
        self.records=frame.to_dict('records')
        self.features=np.asarray(features,dtype=np.float32)
        self.ids=np.asarray(ids,dtype=np.int32)
        self.lengths=np.asarray(lengths,dtype=np.int32)
        self.training=training
        prep=[transforms.Resize((256,256))]
        if training:
            prep.extend([transforms.RandomCrop((224,224)),
                         transforms.RandomHorizontalFlip(),
                         transforms.ColorJitter(brightness=.2,contrast=.2)])
        else:
            prep.append(transforms.CenterCrop((224,224)))
        prep.extend([transforms.ToTensor(),transforms.Normalize(MEAN,STD)])
        self.transform=transforms.Compose(prep)

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        r=self.records[index]
        with Image.open(r['image_path']) as im:
            cropped=crop_bbox_pil(im.convert('RGB'), (r['x'],r['y'],r['w'],r['h']))
            image=self.transform(cropped)
        k=random.randrange(10) if self.training else 0
        return {
            'image':image,
            'input_ids':torch.as_tensor(self.ids[index,k].astype(np.int64)),
            'lengths':torch.as_tensor(self.lengths[index,k].astype(np.int64)),
            'tabular':torch.from_numpy(self.features[index].copy()),
            'label':torch.tensor(int(r['label']),dtype=torch.int64),
            'image_id':torch.tensor(int(r['image_id']),dtype=torch.int64)}


def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % (2**32)
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def make_torch_loaders(manifest, features, ids, lengths, *, batch_size=16, num_workers=0):
    loaders={}
    for name in ('train','val','test'):
        mask=(manifest.split.to_numpy()==name)
        frame=manifest.loc[mask].reset_index(drop=True)
        ds=CUBMultimodalTorch(frame,features[mask],ids[mask],lengths[mask],training=name=='train')
        generator=torch.Generator().manual_seed(SEED)
        loaders[name]=DataLoader(ds,batch_size=batch_size,shuffle=name=='train',
                                 num_workers=num_workers,worker_init_fn=seed_worker,
                                 generator=generator,pin_memory=torch.cuda.is_available())
    return loaders
