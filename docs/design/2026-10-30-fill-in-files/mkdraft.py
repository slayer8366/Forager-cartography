import json,copy
s=json.load(open('../street-v3.json'));d=copy.deepcopy(s);d['name']='Forager Street draft (fill-in study)'
L=d['layers'];ix={l['id']:i for i,l in enumerate(L)}
settled={"id":"landuse_settled","type":"fill","source":"protomaps","source-layer":"landuse",
 "filter":["in",["get","kind"],["literal",["residential","commercial","railway","farmland"]]],
 "paint":{"fill-color":["match",["get","kind"],"residential","#d5d1cb","commercial","#e3cfca","railway","#d6d1d4","farmland","#e8eacd","#e2dfda"],
          "fill-opacity":["interpolate",["linear"],["zoom"],6,0.6,9,1]}}
parks={"id":"landuse_parks_fill","type":"fill","source":"protomaps","source-layer":"landuse",
 "filter":["in",["get","kind"],["literal",["park","recreation_ground","garden","dog_park","pitch"]]],
 "paint":{"fill-color":"#cde5bf"}}
L.insert(ix['landcover']+1,settled); L.insert(ix['landcover']+2,parks)
MW=["interpolate",["exponential",1.6],["zoom"],6,0,8,0.8,10,1.3,12,1.9,15,3,18,13]
for l in L:
  if l['id'] in ('roads_major','roads_bridges_major'):
    l['paint']['line-width']=MW
    l['paint']['line-color']=["match",["get","kind_detail"],["trunk","trunk_link"],"#f2bf72","primary","#f5d28c","secondary","#f8e3ae","tertiary","#ffffff","#f6d68f"]
  if l['id'] in ('roads_major_casing_early','roads_major_casing_late','roads_bridges_major_casing'):
    l['paint']['line-gap-width']=MW
    if l['id']=='roads_major_casing_early': l['paint']['line-width']=["interpolate",["linear"],["zoom"],7.5,0,8.5,0.6,12,1]
    l['paint']['line-color']=["match",["get","kind_detail"],["tertiary","tertiary_link"],"#a39b8d","#b4924c"]
  if l['id']=='roads_minor': l['paint']['line-width']=["interpolate",["exponential",1.6],["zoom"],11,0.3,12,0.7,15,2,18,11]
  if l['id']=='roads_minor_casing': l['paint']['line-gap-width']=["interpolate",["exponential",1.6],["zoom"],11,0.3,12,0.7,15,2,18,11]; l['paint']['line-width']=["interpolate",["linear"],["zoom"],11,0,12,0.6]
  if l['id']=='roads_rail': l['paint']['line-opacity']=0.85; l['paint']['line-color']='#8e979a'
json.dump(d,open('draft.json','w'))
