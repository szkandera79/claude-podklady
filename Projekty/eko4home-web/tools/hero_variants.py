import sys,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
S,OUT=sys.argv[1],sys.argv[2]
W,H=1500,1000
cut=Image.open(f'{S}/cutout_full.png'); cut=cut.crop(cut.getchannel('A').getbbox())
sc=1120/cut.width; cut=cut.resize((int(cut.width*sc),int(cut.height*sc)),Image.LANCZOS)
CX=(W-cut.width)//2; FLOOR=890; CY=FLOOR-cut.height
# key x positions (scaled from source coords; source bbox x0=48)
TB=CY+int((798-208)*sc); FT=TB-28
from PIL import ImageFont
FONT=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',26)
X=lambda sx: CX+int((sx-48)*sc)
def grad(c1,c2,vertical=True):
  a=np.linspace(0,1,H if vertical else W)
  c1,c2=np.array(c1,float),np.array(c2,float)
  g=c1+(c2-c1)*a[:,None]
  img=np.repeat(g[:,None,:],W,1) if vertical else np.repeat(g[None,:,:],H,0)
  return Image.fromarray(img.astype('uint8'))
def radial(cx,cy,r,inner,outer,base=None):
  yy,xx=np.mgrid[0:H,0:W]; d=np.clip(np.hypot(xx-cx,yy-cy)/r,0,1)[...,None]
  i,o=np.array(inner,float),np.array(outer,float)
  return Image.fromarray((i+(o-i)*d).astype('uint8'))
def shadows(img,alpha=120,blur=16):
  sh=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
  d.ellipse([X(40),FLOOR-22,X(380),FLOOR+26],fill=(0,0,0,alpha))
  d.ellipse([X(760),TB-16,X(1020),TB+18],fill=(0,0,0,alpha))
  return Image.alpha_composite(img.convert('RGBA'),sh.filter(ImageFilter.GaussianBlur(blur)))
def put(img,reflect=False):
  img=img.convert('RGBA')
  if reflect:
    r=cut.transpose(Image.FLIP_TOP_BOTTOM); a=np.asarray(r).copy()
    fade=np.linspace(0.28,0,a.shape[0])[:,None]; a[...,3]=(a[...,3]*fade).astype('uint8')
    img.alpha_composite(Image.fromarray(a),(CX,FLOOR+4))
  img.alpha_composite(cut,(CX,CY)); return img.convert('RGB')
def save(img,name): img.save(f'{OUT}/{name}.webp',quality=88); print(name)

# A – světlá zelená (styl webu)
a=radial(W*.5,H*.42,W*.75,(255,255,255),(207,230,215))
d=ImageDraw.Draw(a); d.rectangle([0,FT,W,H],fill=(226,240,231))
save(put(shadows(a)),'A-svetla-zelena')

# B – venku / uvnitř
b=Image.new('RGB',(W,H)); d=ImageDraw.Draw(b)
wall_x=X(500)
b.paste(grad((214,233,247),(244,249,252)).crop((0,0,wall_x,H)),(0,0))
b.paste(grad((246,240,232),(236,227,215)).crop((0,0,W-wall_x,H)),(wall_x,0))
d.rectangle([0,FT,wall_x,H],fill=(110,165,85)); d.rectangle([0,FT,wall_x,FT+10],fill=(140,190,105))
d.rectangle([wall_x,FT,W,H],fill=(214,200,182))
# wall section
d.rectangle([wall_x-28,60,wall_x+28,H],fill=(228,224,218)); d.rectangle([wall_x-28,60,wall_x-22,H],fill=(205,200,193)); d.rectangle([wall_x+22,60,wall_x+28,H],fill=(205,200,193))
for y in range(80,H,46): d.line([wall_x-22,y,wall_x+22,y],fill=(215,211,205),width=2)
# sun + labels
d.ellipse([90,80,190,180],fill=(255,206,64))
b=put(shadows(b,100))
d=ImageDraw.Draw(b)
for txt,x in (('VENKU',70),('UVNITŘ',wall_x+60)):
  y=H-70; w=d.textlength(txt,font=FONT)+36
  d.rounded_rectangle([x,y,x+w,y+46],14,fill=(255,255,255)); d.text((x+18,y+9),txt,font=FONT,fill=(31,77,51))
save(b,'B-venku-uvnitr')

# C – tmavá prémiová
c=radial(W*.5,H*.38,W*.7,(52,110,74),(12,34,22))
d=ImageDraw.Draw(c); d.rectangle([0,FT,W,H],fill=(14,38,25))
cimg=shadows(c,170,20)
save(put(cimg,reflect=True),'C-tmava-premiova')

# D – sluníčko
dd=radial(W*.86,H*.1,W*.95,(255,232,150),(255,250,240))
d=ImageDraw.Draw(dd)
sx,sy=W-170,150
for k in range(16):
  ang=k*math.pi/8; d.polygon([(sx+70*math.cos(ang-.12),sy+70*math.sin(ang-.12)),(sx+118*math.cos(ang),sy+118*math.sin(ang)),(sx+70*math.cos(ang+.12),sy+70*math.sin(ang+.12))],fill=(255,196,30))
d.ellipse([sx-62,sy-62,sx+62,sy+62],fill=(255,200,40))
d.rectangle([0,FT,W,H],fill=(232,243,226))
save(put(shadows(dd,95)),'D-slunicko')

# E – bílé studio s odrazem
e=grad((255,255,255),(238,241,239))
d=ImageDraw.Draw(e); d.rectangle([0,FT,W,H],fill=(246,248,247))
save(put(shadows(e,90),reflect=True),'E-bile-studio')
