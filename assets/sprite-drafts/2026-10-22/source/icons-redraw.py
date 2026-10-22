"""Scratch only (sage-04, ruling 6a). Two new drafts each for trailhead and viewpoint, added to the day sprite
beside the sage-03 drafts: trailhead_b (walker with a pole), trailhead_c (fingerpost with two arms),
viewpoint_b (eye), viewpoint_c (binoculars). Same 19 px rounded box, ring and fill as the others."""
import json, math
from PIL import Image, ImageDraw
S='/tmp/sage04-scratch'
RING=(79,160,116,255); FILL=(214,242,227,255)
def icon(scale, glyph):
    n=19*scale; im=Image.new('RGBA',(n,n),(0,0,0,0)); d=ImageDraw.Draw(im); w=1*scale
    d.rounded_rectangle([0,0,n-1,n-1],radius=4*scale,fill=FILL,outline=RING,width=w); glyph(d,scale,w); return im
def g_walker(d,s,w):   # a walker: head, body leaning forward, two legs mid-stride, one pole
    d.ellipse([8.5*s,3*s,11.5*s,6*s],fill=RING)
    d.line([(10*s,6*s),(9*s,11*s)],fill=RING,width=w+1)                 # body
    d.line([(9*s,11*s),(6.5*s,15.5*s)],fill=RING,width=w+1)             # back leg
    d.line([(9*s,11*s),(12*s,13*s),(12.5*s,16*s)],fill=RING,width=w+1)  # front leg
    d.line([(10*s,8*s),(13*s,9*s)],fill=RING,width=w)                   # arm
    d.line([(13*s,9*s),(14.5*s,16*s)],fill=RING,width=w)                # pole
def g_fingerpost(d,s,w):  # a post with two pointing arms
    d.line([(9.5*s,5*s),(9.5*s,16*s)],fill=RING,width=w+1)
    d.polygon([(5*s,5*s),(12*s,5*s),(14*s,7*s),(12*s,9*s),(5*s,9*s)],outline=RING,width=w)       # arm right
    d.polygon([(14*s,10*s),(7*s,10*s),(5*s,12*s),(7*s,14*s),(14*s,14*s)],outline=RING,width=w)   # arm left
def g_eye(d,s,w):
    d.polygon([(3*s,9.5*s),(9.5*s,4.5*s),(16*s,9.5*s),(9.5*s,14.5*s)],outline=RING,width=w)  # lid, drawn as a lens
    d.ellipse([7*s,7*s,12*s,12*s],fill=RING)
def g_binoculars(d,s,w):
    for cx in (6.5,12.5):
        d.rounded_rectangle([(cx-2.5)*s,7*s,(cx+2.5)*s,15*s],radius=1.5*s,outline=RING,width=w)
        d.rectangle([(cx-1.5)*s,4*s,(cx+1.5)*s,7*s],outline=RING,width=w)
    d.line([(9*s,9*s),(10*s,9*s)],fill=RING,width=w)
NEW=[('trailhead_b',g_walker),('trailhead_c',g_fingerpost),('viewpoint_b',g_eye),('viewpoint_c',g_binoculars)]
for suffix,sc in (('',1),('@2x',2)):
    idx=json.load(open(f'{S}/sprite/light{suffix}.json')); base=Image.open(f'{S}/sprite/light{suffix}.png').convert('RGBA')
    W,H=base.size; out=Image.new('RGBA',(W,H+21*sc),(0,0,0,0)); out.paste(base,(0,0)); x,y=0,H+1*sc
    for name,g in NEW:
        im=icon(2,g); im=im if sc==2 else im.resize((19,19),Image.LANCZOS)
        assert name not in idx; out.paste(im,(x,y)); idx[name]={'x':x,'y':y,'width':19*sc,'height':19*sc,'pixelRatio':sc}; x+=20*sc
    out.save(f'{S}/sprite/light{suffix}.png'); json.dump(idx,open(f'{S}/sprite/light{suffix}.json','w'),indent=1); print(suffix or '1x',out.size,len(idx))
