import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from scipy import ndimage as nd
S='/private/tmp/claude-501/-Users-jindrichszkandera-Library-Mobile-Documents-com-apple-CloudDocs-Claude-Projekty/a41b746a-ee17-4b1b-bd1d-edd58aae5195/scratchpad/wt'
P='/Users/jindrichszkandera/Claude/Projekty/eko4home-web'
src=Image.open(f'{S}/src.webp').convert('RGB'); SW,SH=src.size
A=np.asarray(src).astype(int); chroma=A.max(2)-A.min(2)
def masked(poly_fn):
  m=Image.new('L',(SW,SH),0); poly_fn(ImageDraw.Draw(m)); return m
# unit cutout
um=masked(lambda d:(d.polygon([(50,368),(296,351),(362,355),(364,818),(300,831),(52,772)],fill=255)))
unit=src.convert('RGBA'); unit.putalpha(um.filter(ImageFilter.GaussianBlur(.8))); unit=unit.crop((48,349,366,834))
# tank + fittings cutout
tm=masked(lambda d:(d.rectangle([772,228,1012,790],fill=255),d.ellipse([772,210,1012,250],fill=255),d.ellipse([776,772,1008,798],fill=255)))
fm=np.zeros((SH,SW),bool)
for y in (418,570,628,703): fm[y-16:y+17,748:775]=True
red_=(A[...,0]-A[...,1]>70)&(A[...,0]>140); blue_=(A[...,2]-A[...,0]>18)&(A[...,2]>70)
fm&=(chroma>28)&~red_&~blue_; fm=nd.binary_closing(nd.binary_opening(fm,iterations=1),iterations=2)
M=(np.asarray(tm)>0)|fm
tank=src.convert('RGBA'); tank.putalpha(Image.fromarray((M*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.8))); tank=tank.crop((740,205,1016,800))

bg=Image.open(f'{P}/assets/src-orig/k-ohrev-vody.webp').convert('RGB')
B=np.asarray(bg).astype(float); H,W,_=B.shape
R_,G_,B_=B[...,0],B[...,1],B[...,2]; yy,xx=np.mgrid[0:H,0:W]
s=1.05
# target geometry
tank_x=int(321+(740-217)*s); tank_y=int(205*s-50)
u_s=s*0.85; uw,uh=int(unit.width*u_s),int(unit.height*u_s)
u_bottom=int(831*s-50)       # same floor contact as before (~822)
u_cx=int(321+206*s)
ux,uy=386,u_bottom-uh
# inpaint: green glow lines + original white unit
green=(G_-(R_+B_)/2>6)&(xx>=680)&(xx<=1000)&(yy>=200)&(yy<=740)
oldunit=(xx>=378)&(xx<=698)&(yy>=440)&(yy<=790)
hole=nd.binary_dilation(green,iterations=7)|((xx>=380)&(xx<=708)&(yy>=436)&(yy<=800))
out=B.copy()
for c in range(3):
  ch=out[...,c].copy(); ch[hole]=np.nan
  for y in np.where(hole.any(1))[0]:
    row=ch[y]; ok=~np.isnan(row); idx=np.arange(W); ch[y,~ok]=np.interp(idx[~ok],idx[ok],row[ok])
  for _ in range(900):
    sm=nd.uniform_filter(ch,5); ch[hole]=sm[hole]
  out[...,c]=ch
# clone strips beside the old unit (wall/slab continue horizontally)
img=Image.fromarray(out.clip(0,255).astype('uint8')).convert('RGBA')

# shadows (sun from left -> cast slightly right)
sh=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
d.polygon([(ux+10,u_bottom-6),(ux+uw+60,u_bottom-14),(ux+uw+90,u_bottom+18),(ux+20,u_bottom+22)],fill=(30,25,20,120))
d.ellipse([tank_x+10,int(790*s-50)-14,tank_x+tank.width*s+30,int(790*s-50)+20],fill=(30,25,20,110))
img=Image.alpha_composite(img,sh.filter(ImageFilter.GaussianBlur(14)))
ao=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ao)
d.rectangle([ux+8,u_bottom-5,ux+uw-4,u_bottom+5],fill=(0,0,0,150))
img=Image.alpha_composite(img,ao.filter(ImageFilter.GaussianBlur(4)))

# pipes – black insulated, drawn supersampled
SS=3; L=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); dp=ImageDraw.Draw(L)
fit_y=[int(y*s-50) for y in (628,703)]      # flow/return fittings
fit_x=int(321+(752-217)*s)
def pipe(pts,w=15,band=None):
  P2=[(x*SS,y*SS) for x,y in pts]
  for col,ww,off in [((10,10,10,255),w+2,1.5),((38,38,40,255),w,0),((78,78,82,255),w*0.35,-w*0.25)]:
    q=[(x,y+off*SS) for x,y in P2]; dp.line(q,fill=col,width=int(ww*SS),joint='curve')
    for x,y in q: r=ww*SS/2; dp.ellipse([x-r,y-r,x+r,y+r],fill=col)
  if band:
    x,y=pts[-1]; dp.rectangle([(x-26)*SS,(y-w/2-1)*SS,(x-18)*SS,(y+w/2+1)*SS],fill=band)
ox=ux+uw-6                                   # unit right side
pipe([(ox,u_bottom-95),(ox+70,u_bottom-95),(ox+70,u_bottom-60) ,(fit_x-60,u_bottom-60),(fit_x-60,fit_y[0]),(fit_x+6,fit_y[0])],band=(200,40,35,255))
pipe([(ox,u_bottom-60),(ox+40,u_bottom-60),(ox+40,u_bottom-30),(fit_x-30,u_bottom-30),(fit_x-30,fit_y[1]),(fit_x+6,fit_y[1])],band=(40,70,200,255))
L=L.resize((W,H),Image.LANCZOS)
img=Image.alpha_composite(img,L)

# unit: scale + light match (warm, softer contrast, top-left light)
u=unit.resize((uw,uh),Image.LANCZOS)
rgb=u.convert('RGB'); rgb=ImageEnhance.Contrast(rgb).enhance(.9); a=np.asarray(rgb).astype(float)
a*=np.array([1.04,1.0,0.94]); a=a*0.92+np.array([22,20,16])
g=np.linspace(1.12,0.9,uw)[None,:,None]*np.linspace(1.05,0.95,uh)[:,None,None]
a=np.clip(a*g,0,255)
u2=Image.fromarray(a.astype('uint8')).convert('RGBA'); u2.putalpha(u.getchannel('A')); u2=u2.filter(ImageFilter.GaussianBlur(.35))
img.alpha_composite(u2,(ux,uy))
t=tank.resize((int(tank.width*s),int(tank.height*s)),Image.LANCZOS)
img.alpha_composite(t,(tank_x,tank_y))

from PIL import ImageFont
FT=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',22)
G=Image.new('RGBA',(W,H),(0,0,0,0)); dg=ImageDraw.Draw(G)
tx_r=tank_x+int(tank.width*s)-28   # tank right edge
yH=int(650*s-50)
path=[(tx_r,yH),(1245,yH),(1245,742)]
quad=[(1255,742),(1575,742),(1605,792),(1235,792)]
def mapq(u,v):
  (x0,y0),(x1,y1),(x2,y2),(x3,y3)=quad
  top=(x0+(x1-x0)*u,y0+(y1-y0)*u); bot=(x3+(x2-x3)*u,y3+(y2-y3)*u)
  return (top[0]+(bot[0]-top[0])*v, top[1]+(bot[1]-top[1])*v)
serp=[]; n=7
for i in range(n+1):
  u=0.05+0.9*i/n; vs=(0.08,0.92) if i%2==0 else (0.92,0.08)
  serp+= [mapq(u,vs[0]),mapq(u,vs[1])]
for col,w,bl in (((255,120,40,90),18,8),((255,150,60,200),6,0),((255,220,170,255),2,0)):
  L2=Image.new('RGBA',(W,H),(0,0,0,0)); d2=ImageDraw.Draw(L2)
  d2.line(path+[mapq(0.05,0.08)],fill=col,width=w,joint='curve'); d2.line(serp,fill=col,width=w,joint='curve')
  G=Image.alpha_composite(G,L2.filter(ImageFilter.GaussianBlur(bl)) if bl else L2)
dg=ImageDraw.Draw(G)
ax,ay=1185,yH; dg.polygon([(ax+14,ay),(ax-6,ay-10),(ax-6,ay+10)],fill=(255,150,60,255))
img=Image.alpha_composite(img,G)
def icon_floor(d,x,y,c=(224,102,43)):
  for k in range(3):
    xx=x+4+k*9; d.line([(xx,y+2),(xx+3,y+6),(xx,y+10)],fill=c,width=2)
  d.line([(x,y+14),(x+30,y+14)],fill=c,width=2)
  d.line([(x+2,y+19),(x+26,y+19),(x+28,y+21),(x+26,y+24),(x+4,y+24),(x+2,y+26),(x+4,y+29),(x+30,y+29)],fill=c,width=2)
def icon_rad(d,x,y,c=(194,75,42)):
  for k in range(3): d.rounded_rectangle([x+k*10,y+6,x+k*10+7,y+30],3,outline=c,width=2)
  d.line([(x+8,y+1),(x+9,y+4)],fill=c,width=2); d.line([(x+18,y+1),(x+19,y+4)],fill=c,width=2)
def pill(x,y,txt,icons=()):
  d=ImageDraw.Draw(img); iw=len(icons)*40; w=d.textlength(txt,font=FT)+28+iw
  d.rounded_rectangle([x,y,x+w,y+44],12,fill=(255,255,255,240))
  for k,f in enumerate(icons): f(d,x+12+k*40,y+7)
  d.text((x+14+iw,y+10),txt,font=FT,fill=(31,77,51))
pill(1275,296,'Teplá voda (TUV)')
pill(1275,yH-60,'Topení: podlaha / radiátory',(icon_floor,icon_rad))
img.convert('RGB').save(f'{S}/ohrev_v2.jpg',quality=92)
print(ux,uy,uw,uh,tank_x,tank_y,fit_x,fit_y)
