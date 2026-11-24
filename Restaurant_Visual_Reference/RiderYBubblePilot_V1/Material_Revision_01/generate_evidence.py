"""Generate acceptance evidence for RiderY Material_Revision_01."""
import sys, os, json, hashlib
sys.path.insert(0, r'C:/Users/Administrator/WorkBuddy/2026-11-23-00-25-17/.pylibs')
import numpy as np
from PIL import Image, ImageDraw

PILOT = r'C:/Users/Administrator/WorkBuddy/cooking-review-publish/Restaurant_Visual_Reference/RiderYBubblePilot_V1'
OUT = os.path.join(PILOT, 'Material_Revision_01')
BG = r'E:/un/u/My project (1)/Assets/Resources/Art/Restaurant/restaurant_full.jpg'
CX, CY, CW, CH = 795, 340, 265, 160

orig = Image.open(os.path.join(PILOT, 'original_bubble_crop.png')).convert('RGB')
base = Image.open(os.path.join(PILOT, 'bubble_riderY_clean_candidate.png')).convert('RGB')
rev  = Image.open(os.path.join(OUT, 'bubble_riderY_clean_rev01.png')).convert('RGB')
O, Ba, Re = [np.asarray(x) for x in (orig, base, rev)]

def md5(path):
    return hashlib.md5(open(path,'rb').read()).hexdigest()

def zoom(im, box, scale, annotate=False):
    x0,y0,x1,y1 = box
    c = im.crop((x0,y0,x1,y1))
    z = c.resize(((x1-x0)*scale,(y1-y0)*scale), Image.NEAREST)
    if annotate:
        d = ImageDraw.Draw(z)
        for x in range(x0,x1+1,5):
            px=(x-x0)*scale
            d.line([(px,0),(px,z.height)],fill=(255,0,255))
            if x%10==0: d.text((px+2,2),str(x),fill=(180,0,180))
        for y in range(y0,y1+1,2):
            py=(y-y0)*scale
            d.line([(0,py),(z.width,py)],fill=(0,140,255))
            d.text((2,py+2),str(y),fill=(0,90,180))
    return z

def hstack(images, gap=12, bg=(255,255,255)):
    w=sum(i.width for i in images)+gap*(len(images)-1)
    h=max(i.height for i in images)
    out=Image.new('RGB',(w,h),bg); x=0
    for im in images:
        out.paste(im,(x,0)); x+=im.width+gap
    return out

def vstack(images, gap=10, bg=(255,255,255)):
    w=max(i.width for i in images); h=sum(i.height for i in images)+gap*(len(images)-1)
    out=Image.new('RGB',(w,h),bg); y=0
    for im in images:
        out.paste(im,(0,y)); y+=im.height+gap
    return out

# 1) Three-way full-crop side by side, 4x
lbl = lambda s: Image.new('RGB',(CW*4,26),(245,245,245))
three = hstack([zoom(orig,(0,0,CW,CH),4), zoom(base,(0,0,CW,CH),4), zoom(rev,(0,0,CW,CH),4)])
three.save(os.path.join(OUT,'three_way_4x.png'))

# 2) Bottom region 4x and 8x, candidate vs revision (annotated), crop-space box
box4=(55,74,175,95)   # bg x850..970 y414..435
box8=(55,78,175,92)   # bg x850..970 y418..432
b4 = hstack([zoom(base,box4,4,True), zoom(rev,box4,4,True)])
b4.save(os.path.join(OUT,'bottom_compare_4x.png'))
b8 = vstack([
    hstack([zoom(base,box8,8,True), zoom(rev,box8,8,True)]),
])
b8.save(os.path.join(OUT,'bottom_compare_8x.png'))

# 3) Stroke protection comparison: tight crop around bottom stroke, 8x, no grid
stroke_box=(60,84,165,100)  # bg x855..960 y424..440
sp = hstack([
    zoom(orig,stroke_box,8),
    zoom(base,stroke_box,8),
    zoom(rev,stroke_box,8),
])
sp.save(os.path.join(OUT,'stroke_protection_8x.png'))

# 4) Change map: per-pixel difference amplified
D = np.abs(Re.astype(int)-Ba.astype(int)).max(2)
cm = np.zeros((CH,CW,3),np.uint8)
cm[D>0]=[255,40,40]
cm[D>8]=[255,140,40]
cm[D>24]=[255,220,60]
zoom(Image.fromarray(cm),(55,74,175,95),8).save(os.path.join(OUT,'change_map_8x.png'))

# 5) Paste-back on original background: candidate vs revision
bgim = Image.open(BG).convert('RGB')
def pasteback(tile,name):
    im=bgim.copy(); im.paste(tile,(CX,CY))
    im.crop((CX+40,CY+70,CX+225,CY+110)).resize((185*4,40*4),Image.NEAREST).save(os.path.join(OUT,name))
pasteback(base,'pasteback_base_bottom_4x.png')
pasteback(rev,'pasteback_rev_bottom_4x.png')
# full bubble pasteback for context
full=bgim.copy(); full.paste(rev,(CX,CY))
full.crop((CX-10,CY-15,CX+CW+10,CY+CH+10)).resize(((CW+20)*2,(CH+25)*2),Image.LANCZOS).save(os.path.join(OUT,'pasteback_rev_full_2x.png'))

# 6) Edge diff report (max per edge, plus count)
edges = {
 'top': int(np.abs(Re[0].astype(int)-Ba[0].astype(int)).max()),
 'bottom': int(np.abs(Re[-1].astype(int)-Ba[-1].astype(int)).max()),
 'left': int(np.abs(Re[:,0].astype(int)-Ba[:,0].astype(int)).max()),
 'right': int(np.abs(Re[:,-1].astype(int)-Ba[:,-1].astype(int)).max()),
}
# also vs original crop, since original crop edges should be preserved
edges_vs_orig = {
 'top': int(np.abs(Re[0].astype(int)-O[0].astype(int)).max()),
 'bottom': int(np.abs(Re[-1].astype(int)-O[-1].astype(int)).max()),
 'left': int(np.abs(Re[:,0].astype(int)-O[:,0].astype(int)).max()),
 'right': int(np.abs(Re[:,-1].astype(int)-O[:,-1].astype(int)).max()),
}
stats = json.load(open(os.path.join(OUT,'revision_stats.json'),encoding='utf-8'))
stats.update({
 'md5_base': md5(os.path.join(PILOT,'bubble_riderY_clean_candidate.png')),
 'md5_rev': md5(os.path.join(OUT,'bubble_riderY_clean_rev01.png')),
 'md5_orig_crop': md5(os.path.join(PILOT,'original_bubble_crop.png')),
 'edges_vs_base': edges,
 'edges_vs_original_crop': edges_vs_orig,
})
with open(os.path.join(OUT,'revision_stats.json'),'w',encoding='utf-8') as f:
    json.dump(stats,f,ensure_ascii=False,indent=2)
print(json.dumps(stats,ensure_ascii=False,indent=2))
