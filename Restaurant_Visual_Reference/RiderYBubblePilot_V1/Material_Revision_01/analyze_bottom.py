"""RiderY Material_Revision_01: read-only analysis of bottom inner-rim residue.

Loads the preserved original crop and the current 7aa672cf candidate from the
published pilot, then reports the color/geometry of the bottom arc region so
plate residue can be separated from the natural inner shadow and the dark
brown bubble outline. No files are overwritten here.
"""
import sys, os, json
sys.path.insert(0, r'C:/Users/Administrator/WorkBuddy/2026-11-23-00-25-17/.pylibs')
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PILOT = r'C:/Users/Administrator/WorkBuddy/cooking-review-publish/Restaurant_Visual_Reference/RiderYBubblePilot_V1'
OUT = os.path.join(PILOT, 'Material_Revision_01')
CX, CY, CW, CH = 795, 340, 265, 160

orig = np.asarray(Image.open(os.path.join(PILOT, 'original_bubble_crop.png')).convert('RGB')).astype(np.int16)
cand = np.asarray(Image.open(os.path.join(PILOT, 'bubble_riderY_clean_candidate.png')).convert('RGB')).astype(np.int16)
H, W, _ = orig.shape
yy, xx = np.mgrid[0:H, 0:W]
gx, gy = xx + CX, yy + CY

def dark_stroke(a):
    R, G, B = a[:,:,0], a[:,:,1], a[:,:,2]
    return (R < 170) & (G < 125) & (B < 100) & ((R-G) > 14) & ((G-B) > 4)

def greenish(a):
    R, G, B = a[:,:,0], a[:,:,1], a[:,:,2]
    return (G >= R - 6) & (G > B + 12) & (G > 95) & (B < 190)

dark_o, dark_c = dark_stroke(orig), dark_stroke(cand)
grn_o, grn_c = greenish(orig), greenish(cand)

# Region requested by the reviewer, in bg coords: x 850..960, y 423..427.
rx = (gx >= 840) & (gx <= 970)
ry = (gy >= 416) & (gy <= 440)
region = rx & ry

report = {'crop': [CX, CY, CW, CH], 'rows': []}
for ybg in range(416, 441):
    row = (gy == ybg)
    sel = row & rx
    if not sel.any():
        continue
    o, c = orig[sel], cand[sel]
    report['rows'].append({
        'bg_y': ybg,
        'orig_dark': int(dark_o[sel].sum()),
        'cand_dark': int(dark_c[sel].sum()),
        'orig_green': int(grn_o[sel].sum()),
        'cand_green': int(grn_c[sel].sum()),
        'orig_median': np.median(o, axis=0).astype(int).tolist(),
        'cand_median': np.median(c, axis=0).astype(int).tolist(),
    })

# Stroke boundary along the bottom: first dark pixel scanning up from y=445 at
# each x, both for original and candidate, to confirm stroke is untouched.
stroke_profile = []
for xbg in range(845, 966, 5):
    col = (gx == xbg)
    ys_o = np.where(col & dark_o & (gy >= 420) & (gy <= 445))[0]
    ys_c = np.where(col & dark_c & (gy >= 420) & (gy <= 445))[0]
    stroke_profile.append({
        'bg_x': xbg,
        'orig_stroke_top_y': int(gy[ys_o].min()) if len(ys_o) else None,
        'cand_stroke_top_y': int(gy[ys_c].min()) if len(ys_c) else None,
    })
report['stroke_profile'] = stroke_profile

# Sample exact RGB triples across a vertical cut at x=905 (bottom center) and
# x=880, where the residue arc is strongest.
cuts = {}
for xbg in (865, 880, 895, 905, 920, 940):
    col = (gx == xbg)
    cuts[str(xbg)] = []
    for ybg in range(420, 442):
        s = col & (gy == ybg)
        cuts[str(xbg)].append({
            'y': ybg,
            'o': orig[s][0].tolist(),
            'c': cand[s][0].tolist(),
        })
report['vertical_cuts'] = cuts

with open(os.path.join(OUT, 'bottom_analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

# Build an annotated 8x zoom with bg coordinate grid for visual review.
def zoom_annotated(a, title):
    x0, x1, y0, y1 = 840, 970, 416, 442  # bg coords
    crop = a[y0-CY:y1-CY, x0-CX:x1-CX]
    sc = 8
    im = Image.fromarray(crop.astype(np.uint8)).resize(((x1-x0)*sc, (y1-y0)*sc), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for xbg in range(x0, x1+1, 5):
        px = (xbg-x0)*sc
        d.line([(px,0),(px,im.height)], fill=(255,0,255), width=1)
        if xbg % 10 == 0:
            d.text((px+2,2), str(xbg), fill=(180,0,180))
    for ybg in range(y0, y1+1, 2):
        py = (ybg-y0)*sc
        d.line([(0,py),(im.width,py)], fill=(0,140,255), width=1)
        d.text((2,py+2), str(ybg), fill=(0,90,180))
    im.save(os.path.join(OUT, title))

zoom_annotated(orig, 'orig_bottom_annotated_8x.png')
zoom_annotated(cand, 'candidate_bottom_annotated_8x.png')

print(json.dumps({
    'rows_selected': report['rows'],
    'stroke_profile': stroke_profile,
}, ensure_ascii=False, indent=2))
