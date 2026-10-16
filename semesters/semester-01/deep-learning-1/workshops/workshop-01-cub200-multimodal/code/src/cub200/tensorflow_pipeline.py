"""Pipeline TensorFlow verdaderamente nativo: tf.io + tf.image + tf.data.

No usa tf.py_function ni llama DataLoaders de PyTorch.
"""
from __future__ import annotations
import numpy as np
from .common import MEAN, STD, SEED


def make_tf_datasets(manifest, features, ids, lengths, *, batch_size=16):
    import tensorflow as tf
    tf.random.set_seed(SEED)
    mean=tf.constant(MEAN,dtype=tf.float32)
    std=tf.constant(STD,dtype=tf.float32)
    pipelines={}

    def parse(r, training):
        im=tf.io.decode_jpeg(tf.io.read_file(r['image_path']),channels=3)
        dims=tf.shape(im)
        H,W=dims[0],dims[1]
        x,y,w,h=tf.unstack(r['bbox'])
        x0=tf.clip_by_value(tf.cast(tf.floor(x-0.1*w),tf.int32),0,W-1)
        y0=tf.clip_by_value(tf.cast(tf.floor(y-0.1*h),tf.int32),0,H-1)
        x1=tf.clip_by_value(tf.cast(tf.math.ceil(x+1.1*w),tf.int32),x0+1,W)
        y1=tf.clip_by_value(tf.cast(tf.math.ceil(y+1.1*h),tf.int32),y0+1,H)
        im=tf.image.crop_to_bounding_box(im,y0,x0,y1-y0,x1-x0)
        im=tf.image.resize(tf.image.convert_image_dtype(im,tf.float32),[256,256])
        if training:
            im=tf.image.random_crop(im,[224,224,3])
            im=tf.image.random_flip_left_right(im)
            im=tf.image.random_brightness(im,max_delta=.2)
            im=tf.image.random_contrast(im,lower=.8,upper=1.2)
            k=tf.random.uniform([],minval=0,maxval=10,dtype=tf.int32)
        else:
            im=tf.image.crop_to_bounding_box(im,16,16,224,224)
            k=tf.constant(0,tf.int32)
        im=tf.ensure_shape((tf.clip_by_value(im,0.,1.)-mean)/std,[224,224,3])
        return {'image':im,
                'input_ids':tf.cast(tf.gather(r['input_ids'],k),tf.int64),
                'lengths':tf.cast(tf.gather(r['lengths'],k),tf.int64),
                'tabular':r['tabular'],
                'label':tf.cast(r['label'],tf.int64),
                'image_id':tf.cast(r['image_id'],tf.int64)}

    for name in ('train','val','test'):
        mask=(manifest.split.to_numpy()==name)
        df=manifest.loc[mask]
        arrays={'image_path':df.image_path.astype(str).to_numpy(),
                'bbox':df[['x','y','w','h']].to_numpy(dtype=np.float32),
                'input_ids':ids[mask].astype(np.int32),
                'lengths':lengths[mask].astype(np.int32),
                'tabular':features[mask].astype(np.float32),
                'label':df.label.to_numpy(dtype=np.int64),
                'image_id':df.image_id.to_numpy(dtype=np.int64)}
        dataset=tf.data.Dataset.from_tensor_slices(arrays)
        training=(name=='train')
        if training:
            dataset=dataset.shuffle(len(df),seed=SEED,reshuffle_each_iteration=True)
        dataset=dataset.map(lambda x:parse(x,training),num_parallel_calls=tf.data.AUTOTUNE,
                            deterministic=not training)
        dataset=dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
        pipelines[name]=dataset
    return pipelines
