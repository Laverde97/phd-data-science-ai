"""Contrato de datos y comparaciones que no requieren entrenamiento de redes."""
import numpy as np
from .common import EXPECTED_COUNTS


def audit_prepared(manifest, features, ids, lengths, metadata, *, enforce_full=True):
    n=len(manifest)
    assert n==len(features)==len(ids)==len(lengths)
    assert manifest.image_id.is_unique
    assert features.shape==(n,318)
    assert ids.shape==(n,10,int(metadata['max_len']))
    assert lengths.shape==(n,10)
    assert (ids>=0).all() and np.isfinite(features).all()
    assert (lengths>=1).all() and (lengths<=metadata['max_len']).all()
    assert np.isin(features[:,:312], [0.,1.]).all()
    assert manifest.label.between(0,199).all()
    if enforce_full:
        assert manifest.split.value_counts().to_dict()==EXPECTED_COUNTS
        assert manifest.label.nunique()==200
        assert all(manifest[manifest.split==s].label.nunique()==200 for s in EXPECTED_COUNTS)
    for name in ('train','val','test'):
        ids_set=set(manifest.loc[manifest.split==name,'image_id'])
        assert len(ids_set)==(manifest.split==name).sum()
    return True


def check_batch(batch, *, framework='torch', max_len: int):
    """Acepta outputs Torch o TF en forma de diccionario y comprueba contrato."""
    def ar(x):
        return x.detach().cpu().numpy() if hasattr(x,'detach') else np.asarray(x)
    b=ar(batch['image']).shape[0]
    image_shape=(b,3,224,224) if framework=='torch' else (b,224,224,3)
    assert ar(batch['image']).shape==image_shape
    assert ar(batch['input_ids']).shape==(b,max_len)
    assert ar(batch['lengths']).shape==(b,)
    assert ar(batch['tabular']).shape==(b,318)
    assert ar(batch['label']).shape==(b,)
    assert ar(batch['image_id']).shape==(b,)
    assert np.isfinite(ar(batch['image'])).all() and np.isfinite(ar(batch['tabular'])).all()
    assert ((ar(batch['lengths'])>=1)&(ar(batch['lengths'])<=max_len)).all()
    assert ((ar(batch['label'])>=0)&(ar(batch['label'])<200)).all()
    assert (ar(batch['input_ids'])>=0).all()
    return {'batch_size':b, 'image':image_shape, 'input_ids':(b,max_len),
            'tabular':(b,318), 'state':'OK'}
