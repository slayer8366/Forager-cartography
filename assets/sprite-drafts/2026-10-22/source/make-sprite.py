"""Scratch sprite v5 draft (sage-03): the pinned light sprite plus pattern tiles and six icons. Not the shipped sprite."""
import json, math
from PIL import Image, ImageDraw
A='/home/bwann83/Forager/.claude/worktrees/street-preview/map-style/assets/sprites/v4'
OUT='/tmp/sage03-scratch/sprite'
RING=(79,160,116,255); FILL=(214,242,227,255)
def hexrgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))+(255,)

def tree(d, x, y, s, col):
    """Conifer, s = height in px, apex at (x, y)."""
    w=s*0.9
    d.polygon([(x,y),(x-w/2,y+s*0.78),(x+w/2,y+s*0.78)],fill=col)
    d.rectangle([x-s*0.08,y+s*0.78,x+s*0.08,y+s],fill=col)
def tree_pattern(scale, col, dense):
    c=32*scale; im=Image.new('RGBA',(c,c),(0,0,0,0)); d=ImageDraw.Draw(im)
    s=8*scale
    pts=[(9,6),(25,20)] if dense else [(14,12)]
    for px,py in pts: tree(d,px*scale,py*scale,s,col)
    return im
def irregular_pattern(scale, col):
    c=64*scale; im=Image.new('RGBA',(c,c),(0,0,0,0)); d=ImageDraw.Draw(im); s=8*scale
    for px,py in [(10,6),(41,14),(24,36),(55,46),(5,54)]: tree(d,px*scale,py*scale,s,col)
    return im
def tufts_pattern(scale, col):
    c=32*scale; im=Image.new('RGBA',(c,c),(0,0,0,0)); d=ImageDraw.Draw(im); w=max(1,scale)
    for bx,by in [(5,12),(19,26)]:
        bx*=scale; by*=scale; s=scale
        d.line([bx-4*s,by,bx+4*s,by],fill=col,width=w)          # baseline
        d.line([bx,by,bx,by-5*s],fill=col,width=w)              # centre blade
        d.line([bx-2*s,by,bx-4*s,by-4*s],fill=col,width=w)      # left blade
        d.line([bx+2*s,by,bx+4*s,by-4*s],fill=col,width=w)      # right blade
    return im
def dots_pattern(scale, col):
    c=16*scale; im=Image.new('RGBA',(c,c),(0,0,0,0)); d=ImageDraw.Draw(im); r=0.9*scale
    for px,py in [(4,4),(12,12)]:
        d.ellipse([px*scale-r,py*scale-r,px*scale+r,py*scale+r],fill=col)
    return im

def icon(scale, glyph):
    n=19*scale; im=Image.new('RGBA',(n,n),(0,0,0,0)); d=ImageDraw.Draw(im); w=1*scale
    d.rounded_rectangle([0,0,n-1,n-1],radius=4*scale,fill=FILL,outline=RING,width=w)
    glyph(d, scale, w)
    return im
def g_parking(d,s,w):
    d.line([(7*s,4*s),(7*s,15*s)],fill=RING,width=w+s//2 or w)
    d.line([(7*s,4*s),(10.5*s,4*s)],fill=RING,width=w)
    d.arc([7*s,4*s,13*s,10*s],270,90,fill=RING,width=w)
    d.line([(7*s,10*s),(10.5*s,10*s)],fill=RING,width=w)
def g_camp(d,s,w):
    d.polygon([(9.5*s,4*s),(3*s,15*s),(16*s,15*s)],outline=RING,width=w)
    d.line([(9.5*s,8*s),(7*s,15*s)],fill=RING,width=w); d.line([(9.5*s,8*s),(12*s,15*s)],fill=RING,width=w)
def g_picnic(d,s,w):
    d.line([(4*s,7*s),(15*s,7*s)],fill=RING,width=w)       # table top
    d.line([(3*s,12*s),(16*s,12*s)],fill=RING,width=w)     # bench
    d.line([(7*s,7*s),(4.5*s,15*s)],fill=RING,width=w); d.line([(12*s,7*s),(14.5*s,15*s)],fill=RING,width=w)
def g_viewpoint(d,s,w):
    cx,cy=9.5*s,14*s
    d.pieslice([cx-4*s,cy-4*s,cx+4*s,cy+4*s],180,360,outline=RING,width=w)
    for ang in (205,240,270,300,335):
        a=math.radians(ang); d.line([(cx+5.5*s*math.cos(a),cy+5.5*s*math.sin(a)),(cx+9*s*math.cos(a),cy+9*s*math.sin(a))],fill=RING,width=w)
def g_trailhead(d,s,w):
    d.line([(8*s,5*s),(8*s,15*s)],fill=RING,width=w)       # post
    d.polygon([(6*s,5*s),(13*s,5*s),(15*s,7*s),(13*s,9*s),(6*s,9*s)],outline=RING,width=w)   # pointing board
    d.line([(5*s,15*s),(11*s,15*s)],fill=RING,width=w)     # ground
def g_ranger(d,s,w):
    d.polygon([(4*s,10*s),(9.5*s,5*s),(15*s,10*s),(15*s,15*s),(4*s,15*s)],outline=RING,width=w)  # house
    d.rectangle([8*s,11*s,11*s,15*s],outline=RING,width=w)  # door
    d.line([(12.5*s,8*s),(12.5*s,3*s)],fill=RING,width=w); d.polygon([(12.5*s,3*s),(16*s,4.5*s),(12.5*s,6*s)],fill=RING)  # flag

ITEMS=[  # name, size(1x), drawer(scale)
 ('tree_dark_dense',32,lambda sc: tree_pattern(sc,hexrgb('#3e7a3a'),True)),
 ('tree_dark_sparse',32,lambda sc: tree_pattern(sc,hexrgb('#3e7a3a'),False)),
 ('tree_light_dense',32,lambda sc: tree_pattern(sc,hexrgb('#5f9a52'),True)),
 ('tree_light_sparse',32,lambda sc: tree_pattern(sc,hexrgb('#5f9a52'),False)),
 ('tree_dark_irregular',64,lambda sc: irregular_pattern(sc,hexrgb('#3e7a3a'))),
 ('tufts',32,lambda sc: tufts_pattern(sc,hexrgb('#3fa0c8'))),
 ('scrub_dots',16,lambda sc: dots_pattern(sc,hexrgb('#7fa070'))),
 ('trailhead',19,lambda sc: icon(sc,g_trailhead)),('parking',19,lambda sc: icon(sc,g_parking)),
 ('camp_site',19,lambda sc: icon(sc,g_camp)),('picnic_site',19,lambda sc: icon(sc,g_picnic)),
 ('viewpoint',19,lambda sc: icon(sc,g_viewpoint)),('ranger_station',19,lambda sc: icon(sc,g_ranger)),
]
for suffix,sc in (('',1),('@2x',2)):
    idx=json.load(open(f'{A}/light{suffix}.json')); base=Image.open(f'{A}/light{suffix}.png').convert('RGBA')
    W,H=base.size; out=Image.new('RGBA',(W,(114+32+19+64+4)*sc),(0,0,0,0)); out.paste(base,(0,0))
    x,y=0,114*sc; row_h=32
    for name,size,draw in ITEMS:
        if size==19 and y==114*sc: x,y=0,(114+32+1)*sc
        if size==64: x,y=0,(114+32+1+19+1)*sc
        if sc==1: im=draw(2).resize((size,size),Image.LANCZOS)   # draw at 2x, shrink for 1x
        else: im=draw(2)
        assert name not in idx, name
        out.paste(im,(x,y)); idx[name]={'x':x,'y':y,'width':size*sc,'height':size*sc,'pixelRatio':sc}
        x+=(size+1)*sc
    out.save(f'{OUT}/light{suffix}.png'); json.dump(idx,open(f'{OUT}/light{suffix}.json','w'),indent=1)
    print(suffix or '1x', out.size, len(idx))
# a 6x proof sheet of the new items (2x drawn, 3x shown)
sheet=Image.new('RGBA',(len(ITEMS)*80,80),(226,223,218,255)); x=0
idx2=json.load(open(f'{OUT}/light@2x.json')); im2=Image.open(f'{OUT}/light@2x.png')
for name,size,_ in ITEMS:
    e=idx2[name]; c=im2.crop((e['x'],e['y'],e['x']+e['width'],e['y']+e['height']))
    if name.startswith('tree'): bg=Image.new('RGBA',c.size,hexrgb('#a9d39b')); bg.paste(c,(0,0),c); c=bg
    if name=='tufts': bg=Image.new('RGBA',c.size,hexrgb('#c5e3d6')); bg.paste(c,(0,0),c); c=bg
    sheet.paste(c,(x+4,4),c if c.mode=='RGBA' and not name.startswith(('tree','tufts')) else None); x+=80
sheet.resize((sheet.width*2,160),Image.NEAREST).save('/tmp/sage03-scratch/new-sprite-items-x2.png')
