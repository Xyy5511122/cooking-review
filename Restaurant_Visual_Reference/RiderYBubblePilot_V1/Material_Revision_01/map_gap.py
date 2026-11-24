"""Map, per column, the warm-white gap between plate residue and bubble stroke.

Structure top->bottom in the candidate bottom arc:
  cleaned warm-white | green/tan residue | clean warm-white GAP | natural pink shadow | brown stroke
The GAP is the warm run nearest to (just above) the natural shadow / stroke.
"""
import sys, os, json
sys.path.insert(0, r'C:/Users/Administrator/WorkBuddy/2026-11-23-00-25-17/.pylibs')
import numpy as np
from PIL import Image

PILOT = r'C:/Users/Administrator/WorkBuddy/cooking-review-publish/Restaurant_Visual_Reference/RiderYBubblePilot_V1'
OUT = os.path.join(PILOT, 'Material_Revision_01')
CX, CY = 795, 340
cand = np.asarray(Image.open(os.path.join(PILOT, 'bubble_riderY_clean_candidate.png')).convert('RGB')).astype(int)
H, W, _ = cand.shape
yy, xx = np.mgrid[0:H, 0:W]
gx, gy = xx + CX, yy + CY

def warm(p):
    r, g, b = p
    return (r > 234) & (g > 222) & (b > 205) & ((r - b) >= 5) & ((r - b) <= 48) & ((max(r,g,b)-min(r,g,b)) < 58)

def brown(p):
    r, g, b = p
    return (r < 185) & (g < 135) & (b < 118) & (r > g + 18) & (g > b + 5)

def px(xbg, ybg):
    return cand[(gy == ybg) & (gx == xbg)][0]

rows = []
for xbg in range(840, 971):
    rec = {'x': xbg}
    st = next((y for y in range(420, 446) if brown(px(xbg, y))), None)
    rec['stroke_top'] = st
    # Walk upward from just above the stroke; skip the natural pink shadow;
    # the first warm run encountered is the clean GAP below the residue.
    gap_top = gap_bottom = None
    if st is not None:
        y = st - 1
        while y >= 416 and not warm(px(xbg, y)):
            y -= 1
        if y >= 416:
            gap_bottom = y
            while y >= 416 and warm(px(xbg, y)):
                y -= 1
            gap_top = y + 1
    rec['gap_top'] = gap_top
    rec['gap_bottom'] = gap_bottom
    rec['gap_rows'] = (gap_bottom - gap_top + 1) if gap_top is not None else 0
    rec['residue_last'] = (gap_top - 1) if gap_top is not None else None
    rows.append(rec)

with open(os.path.join(OUT, 'gap_map.json'), 'w', encoding='utf-8') as f:
    json.dump(rows, f, indent=2)

print('x    stroke  gap_top..bottom  gap_rows  residue_last')
for rec in rows:
    if rec['x'] % 5 == 0 or rec['gap_top'] is None or rec['gap_rows'] < 2:
        print('%3d  %-7s %-16s %-9s %s' % (
            rec['x'], rec['stroke_top'],
            '%s..%s' % (rec['gap_top'], rec['gap_bottom']),
            rec['gap_rows'], rec['residue_last']))
