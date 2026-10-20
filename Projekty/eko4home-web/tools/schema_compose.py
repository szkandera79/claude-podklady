import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage as nd
bg=Image.open('/Users/jindrichszkandera/Claude/Projekty/eko4home-web/assets/src-orig/k-ohrev-vody.webp').convert('RGB')
A=np.asarray(bg).astype(float); H,W,_=A.shape
R,G,B=A[...,0],A[...,1],A[...,2]
yy,xx=np.mgrid[0:H,0:W]
# green glow lines between unit and tank
green=(G-(R+B)/2>6)&(xx>=680)&(xx<=1000)&(yy>=200)&(yy<=740)
green=nd.binary_dilation(green,iterations=7)
# diffusion inpaint
out=A.copy(); known=~green
for c in range(3):
  ch=out[...,c].copy(); ch[green]=np.nan
  # init with row-wise interpolation
  for y in np.where(green.any(1))[0]:
    row=ch[y]; idx=np.arange(W); ok=~np.isnan(row)
    ch[y,~ok]=np.interp(idx[~ok],idx[ok],row[ok])
  for _ in range(250):
    sm=nd.uniform_filter(ch,5); ch[green]=sm[green]
  out[...,c]=ch
bgc=Image.fromarray(out.clip(0,255).astype('uint8')).convert('RGBA')
cut=Image.open('cutout_cut.png'); s=1.05
cut=cut.resize((int(cut.width*s),int(cut.height*s)),Image.LANCZOS)
dx,dy=321,-50
# shadows
sh=Image.new('RGBA',bgc.size,(0,0,0,0)); d=ImageDraw.Draw(sh)
d.ellipse([dx+40*s,dy+790*s,dx+390*s,dy+845*s],fill=(0,0,0,120))
tx=dx+(772-217)*s
d.ellipse([tx-10,dy+775*s,tx+250*s,dy+805*s],fill=(0,0,0,110))
sh=sh.filter(ImageFilter.GaussianBlur(12))
bgc=Image.alpha_composite(bgc,sh); bgc.alpha_composite(cut,(dx,dy))
bgc.convert('RGB').save('ohrev_new.jpg',quality=92)
