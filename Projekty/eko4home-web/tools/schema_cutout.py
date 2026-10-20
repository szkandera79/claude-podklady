import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage as nd
src=Image.open('src.webp').convert('RGB'); W,H=src.size
m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
d.polygon([(50,368),(296,351),(362,355),(364,818),(300,831),(52,772)],fill=255)
d.rectangle([772,228,1012,790],fill=255); d.ellipse([772,210,1012,250],fill=255); d.ellipse([776,772,1008,798],fill=255)
A=np.asarray(src).astype(int); chroma=A.max(2)-A.min(2)
fm=np.zeros((H,W),bool)
for y in (418,570,628,703): fm[y-16:y+17,748:775]=True
fm&=(chroma>28)
fm=nd.binary_opening(fm,iterations=1); fm=nd.binary_closing(fm,iterations=2)
M=(np.asarray(m)>0)|fm
mask=Image.fromarray((M*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))
cut=src.convert('RGBA'); cut.putalpha(mask)
# pipes layer (supersampled)
SS=3; P=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); dp=ImageDraw.Draw(P)
def pipe(pts,col,hl,sh,w=13):
  pts=[(x*SS,y*SS) for x,y in pts]
  for c,ww,off in [(sh,w,1.5),(col,w-3,0),(hl,4,-3)]:
    q=[(x,y+off*SS) for x,y in pts]
    dp.line(q,fill=c,width=int(ww*SS),joint='curve')
    for x,y in q: r=ww*SS/2; dp.ellipse([x-r,y-r,x+r,y+r],fill=c)
RED=((205,45,40,255),(240,120,110,255),(120,20,20,255))
BLU=((60,70,190,255),(130,140,235,255),(25,30,100,255))
pipe([(340,705),(760,705)],*BLU)
pipe([(665,705),(665,570),(760,570)],*BLU)
pipe([(340,645),(705,645),(705,418),(758,418)],*RED)
pipe([(705,628),(758,628)],*RED)
P=P.resize((W,H),Image.LANCZOS)
out=Image.new('RGBA',(W,H),(0,0,0,0)); out.alpha_composite(P); out.alpha_composite(cut)
a=np.asarray(out); a2=np.concatenate([a[:,:420],a[:,638:]],axis=1)
Image.fromarray(a2).save('cutout_cut.png')
pv=Image.new('RGBA',out.size,(230,240,232,255)); pv.alpha_composite(out); pv.convert('RGB').save('cut_preview.jpg')
