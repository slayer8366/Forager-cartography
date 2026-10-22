"""Scratch only (sage-05). The night sprite with the irregular tree glyph recoloured to each candidate step
around the owner's screenshot target #5d804f (app's current night glyph). Alpha kept; nothing else in the sprite changes."""
import json, shutil, os
import numpy as np
from PIL import Image
S='/tmp/sage05-scratch'
STEPS={'T1':'#688f58','T2':'#638854','T3':'#5d804f','T4':'#57784a','T5':'#527146'}
hexrgb=lambda h:[int(h[i:i+2],16) for i in (1,3,5)]
for tag,col in STEPS.items():
    out=f'{S}/sprite-night-steps/{tag}'; os.makedirs(out,exist_ok=True)
    for suffix in ('','@2x'):
        idx=json.load(open(f'{S}/sprite-night/light{suffix}.json'))
        im=np.array(Image.open(f'{S}/sprite-night/light{suffix}.png').convert('RGBA'))
        for name in ('tree_dark_irregular','tree_dark_sparse','tree_dark_dense'):
            e=idx[name]; ys,xs=slice(e['y'],e['y']+e['height']),slice(e['x'],e['x']+e['width'])
            cell=im[ys,xs]; mask=cell[...,3]>0; cell[mask,:3]=hexrgb(col); im[ys,xs]=cell
        Image.fromarray(im,'RGBA').save(f'{out}/light{suffix}.png'); shutil.copy(f'{S}/sprite-night/light{suffix}.json',f'{out}/light{suffix}.json')
    print(tag,col,'written')
