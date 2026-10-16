import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from PIL import Image
from cub200.common import bbox_geometry, clip_bbox_to_image, crop_bbox_pil, tokenize, fit_text, encode_caption


def test_tokenizer_sin_numeros_ni_puntuacion():
    assert tokenize('Blue-BIRD 42! Wings.') == ['blue','bird','wings']


def test_vocabulary_train_and_padding():
    vocab, max_len = fit_text(['blue bird','blue wings','red bird','green bird'])
    assert vocab['<pad>']==0 and vocab['<unk>']==1
    assert 'green' not in vocab and 'red' not in vocab
    ids,length=encode_caption('blue unknown',vocab,max_len)
    assert len(ids)==max_len and int(length)<=max_len
    assert ids[0]==vocab['blue']


def test_bbox_geometry():
    g=bbox_geometry(10,20,50,40,100,100)
    assert g.shape==(6,) and g.dtype==np.float32
    assert np.isclose(g[0],.35) and np.isclose(g[-1],.2)
    with pytest.raises(ValueError): bbox_geometry(0,0,0,10,100,100)


def test_bbox_crop_with_margin_and_clipping():
    im=Image.new('RGB',(100,100),'white')
    crop=crop_bbox_pil(im,(10,20,50,40),.1)
    assert crop.size==(60,48)
    crop=crop_bbox_pil(im,(0,0,30,30),.1)
    assert crop.size==(33,33)


def test_bbox_geometry_clips_five_pixel_overflow():
    # Anotación encontrada en la ejecución del dataset original: 380 > 375.
    assert clip_bbox_to_image(2,69,457,311,500,375) == (2.,69.,457.,306.)
    g = bbox_geometry(2,69,457,311,500,375)
    assert g.shape == (6,)
    assert np.isfinite(g).all()
    assert np.isclose(g[3], 306 / 375)
    assert np.isclose(g[-1], (457 * 306) / (500 * 375))


def test_bbox_outside_image_rejected():
    with pytest.raises(ValueError,match='sin intersección'):
        bbox_geometry(600,10,30,30,500,375)
    with pytest.raises(ValueError,match='no finita'):
        bbox_geometry(float('nan'),0,10,10,500,375)
    with pytest.raises(ValueError,match='tamaño no positivo'):
        bbox_geometry(5,5,-10,10,500,375)


def test_bbox_clips_left_and_top():
    assert clip_bbox_to_image(-3,-5,10,20,100,100) == (0.,0.,7.,15.)
    g = bbox_geometry(-3,-5,10,20,100,100)
    assert np.all((g[[0,1,2,3,5]] >= 0) & (g[[0,1,2,3,5]] <= 1))
