"""ETL: metadatos originales -> artefactos compartidos auditables.

No modifica datos originales, no entrena clasificadores ni ajusta con val/test.
"""
from __future__ import annotations
from pathlib import Path
import json
import platform

import joblib
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .common import (SEED, CLASS_COUNT, ATTR_COUNT, EXPECTED_COUNTS,
                     bbox_geometry, clip_bbox_to_image, encode_caption, fit_text, load_captions)


def read_table(p: Path, columns, *, dtypes=None):
    return pd.read_csv(p, sep=r'\s+', header=None, names=columns, dtype=dtypes)


def prepare(data_dir: str | Path, output_dir: str | Path):
    data_dir, output_dir = Path(data_dir), Path(output_dir)
    cub = data_dir / 'CUB_200_2011'
    txtroot = data_dir / 'text_c10'
    paths = {'images': cub/'images.txt', 'labels': cub/'image_class_labels.txt',
             'splits': cub/'train_test_split.txt', 'boxes': cub/'bounding_boxes.txt',
             'attrs': cub/'attributes'/'image_attribute_labels.txt'}
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if not txtroot.is_dir(): missing.append(str(txtroot))
    if missing:
        raise FileNotFoundError('Primero descargue/extraiga las dos fuentes:\n'+'\n'.join(missing))
    output_dir.mkdir(parents=True, exist_ok=True)

    images = read_table(paths['images'], ['image_id','relpath'])
    labels = read_table(paths['labels'], ['image_id','class_id'])
    splits = read_table(paths['splits'], ['image_id','is_train'])
    boxes = read_table(paths['boxes'], ['image_id','x','y','w','h'])
    # 3.677.856 filas: leer solo columnas necesarias para minimizar memoria.
    attrs = pd.read_csv(paths['attrs'], sep=r'\s+', header=None,
                        usecols=[0,1,2], names=['image_id','attr_id','is_present','certainty','time'],
                        dtype={0:np.int32,1:np.int16,2:np.int8})
    for name, frame in [('images', images), ('labels', labels), ('splits', splits), ('boxes', boxes)]:
        if frame.image_id.duplicated().any():
            raise ValueError(f'ID de imagen duplicado en {name}')
    if len(images) != 11788:
        raise ValueError(f'El dataset oficial tiene 11788 imágenes; se encontraron {len(images)}')
    if attrs.duplicated(['image_id','attr_id']).any():
        raise ValueError('Existen atributos duplicados image_id/attr_id; se requiere revisar el origen.')
    if not attrs.attr_id.between(1,ATTR_COUNT).all() or not attrs.is_present.isin([0,1]).all():
        raise ValueError('Los atributos deben tener IDs 1..312 y valores 0/1')
    wide = attrs.pivot(index='image_id', columns='attr_id', values='is_present')
    wide = wide.reindex(index=images.image_id, columns=range(1,313))
    if wide.isna().any().any():
        raise ValueError('Se encontraron atributos faltantes para alguna imagen')
    wide.columns = [f'attr_{i:03d}' for i in range(1,313)]
    master = (images.merge(labels,on='image_id',validate='one_to_one')
             .merge(splits,on='image_id',validate='one_to_one')
             .merge(boxes,on='image_id',validate='one_to_one')
             .merge(wide.reset_index(),on='image_id',validate='one_to_one')
             .sort_values('image_id').reset_index(drop=True))
    if len(master)!=11788 or master.class_id.nunique()!=CLASS_COUNT or not master.class_id.between(1,200).all():
        raise ValueError('Número de imágenes o clases incorrecto')
    if master.is_train.sum()!=5994 or (master.is_train==0).sum()!=5794:
        raise ValueError('Train/test oficial no coincide con 5994/5794')
    master['label'] = master['class_id'].astype(int)-1
    train_all = master.loc[master.is_train==1]
    train_idx, val_idx = train_test_split(train_all.index.to_numpy(), test_size=600,
                                         stratify=train_all.label.to_numpy(),random_state=SEED)
    master['split'] = 'test'
    master.loc[train_idx,'split']='train'
    master.loc[val_idx,'split']='val'
    actual = master.split.value_counts().to_dict()
    if actual != EXPECTED_COUNTS:
        raise ValueError(f'Splits inesperados: {actual}')
    if any(master.loc[master.split==s,'label'].nunique()!=200 for s in EXPECTED_COUNTS):
        raise ValueError('La estratificación no mantuvo las 200 clases en todos los splits')

    caption_lines = []
    geometries = []
    clipped_boxes = []
    for r in master.itertuples(index=False):
        img = cub/'images'/r.relpath
        caption = txtroot/Path(r.relpath).with_suffix('.txt')
        if not img.is_file() or not caption.is_file():
            raise FileNotFoundError(f'Pareja imagen/caption faltante: {img} / {caption}')
        with Image.open(img) as image:
            W,H = image.size
        # Auditoría explícita: algunas anotaciones oficiales exceden por píxeles
        # el lienzo. No modificar el archivo original ni el bbox del manifest.
        clipped = clip_bbox_to_image(r.x, r.y, r.w, r.h, W, H)
        original = (float(r.x), float(r.y), float(r.w), float(r.h))
        if any(abs(a-b) > 1e-6 for a,b in zip(original, clipped)):
            clipped_boxes.append({
                'image_id': int(r.image_id), 'relpath': str(r.relpath),
                'image_width': W, 'image_height': H,
                'original_x': original[0], 'original_y': original[1],
                'original_w': original[2], 'original_h': original[3],
                'clipped_x': clipped[0], 'clipped_y': clipped[1],
                'clipped_w': clipped[2], 'clipped_h': clipped[3],
            })
        geometries.append(bbox_geometry(r.x,r.y,r.w,r.h,W,H))
        caption_lines.append(load_captions(caption))

    caption_train = [text for i, captions in enumerate(caption_lines)
                     if master.loc[i, 'split']=='train' for text in captions]
    vocab, max_len = fit_text(caption_train)
    text_ids = np.zeros((len(master),10,max_len),dtype=np.int32)
    text_lengths = np.zeros((len(master),10),dtype=np.int32)
    for i, lines in enumerate(caption_lines):
        for j, text in enumerate(lines):
            text_ids[i,j],text_lengths[i,j] = encode_caption(text,vocab,max_len)
    geometry = np.asarray(geometries,dtype=np.float32)
    scaler = StandardScaler().fit(geometry[master.split=='train'])
    attr_cols = [f'attr_{i:03d}' for i in range(1,313)]
    tabular = np.concatenate([
        master[attr_cols].to_numpy(dtype=np.float32),
        scaler.transform(geometry).astype(np.float32)],axis=1)
    if not np.isfinite(tabular).all() or tabular.shape!=(11788,318):
        raise ValueError('Vector tabular inválido')

    # Se guardan artefactos sin datos de imágenes: reproducibles y fáciles de auditar.
    columns=['image_id','relpath','label','is_train','split','x','y','w','h']
    master[columns].to_csv(output_dir/'manifest.csv',index=False)
    # Reporte persistente para decidir si algún recorte requiere revisión visual.
    audit_cols=['image_id','relpath','image_width','image_height',
                'original_x','original_y','original_w','original_h',
                'clipped_x','clipped_y','clipped_w','clipped_h']
    pd.DataFrame(clipped_boxes, columns=audit_cols).to_csv(
        output_dir/'bbox_clipping_audit.csv', index=False)
    print(f'BBOX_AUDIT: {len(clipped_boxes)} anotaciones recortadas a límites reales; '
          'detalle en artifacts/bbox_clipping_audit.csv')
    np.save(output_dir/'tabular.npy',tabular)
    np.save(output_dir/'text_ids.npy',text_ids)
    np.save(output_dir/'text_lengths.npy',text_lengths)
    (output_dir/'vocab.json').write_text(json.dumps(vocab,ensure_ascii=False,indent=2),encoding='utf-8')
    joblib.dump(scaler,output_dir/'geometry_scaler.joblib')
    metadata={
        'dataset':'CUB-200-2011 + Reed et al. captions',
        'seed':SEED, 'counts':actual,'vocab_size':len(vocab),'max_len':max_len,
        'special_tokens':{'<pad>':0,'<unk>':1},
        'geometry':['cx_over_W','cy_over_H','w_over_W','h_over_H','w_over_h','area_over_WH'],
        'geometry_fit':'train_only', 'vocab_fit':'train_only',
        'caption_rule':'train: random among 10; val/test: first',
        'classes':200,'tabular_dim':318,'bbox_clipping_count':len(clipped_boxes),
        'bbox_policy':'clip_to_visible_image_for_geometry; preserve_raw_bbox_in_manifest',
        'python':platform.python_version(),
        'numpy':np.__version__,'pandas':pd.__version__}
    (output_dir/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(json.dumps(metadata,indent=2,ensure_ascii=False))
    return metadata
