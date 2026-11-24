"""RiderY Material_Revision_01: localized bottom-inner-rim repair.

Base = published candidate 7aa672cf (never overwritten).
Only the residual plate arc at the very bottom inner rim is rebuilt:
  * per-column clean warm-white GAP between residue and natural pink shadow is mapped
  * rows above that GAP (the last green/tan residue rows) are rebuilt with the same
    row-interpolated warm-white model used by build_clean.py, locally offset to match
    the measured GAP color so no seam is introduced
  * alpha is smooth in both axes; no hard cut, no hard-edge mask
  * brown stroke / V tail / natural inner shadow / clean GAP / all four edges are untouched
"""
import sys, os, json
sys.path.insert(0, r'C:/Users/Administrator/WorkBuddy/2026-11-23-00-25-17/.pylibs')
import numpy as np
from PIL import Image, ImageDraw

PILOT = r'C:/Users/Administrator/WorkBuddy/cooking-review-publish/Restaurant_Visual_Reference/RiderYBubblePilot_V1'
OUT = os.path.join(PILOT, 'Material_Revision_01')
CX, CY, CW, CH = 795, 340, 265, 160

orig = np.asarray(Image.open(os.path.join(PILOT, 'original_bubble_crop.png')).convert('RGB')).astype(np.float64)
base = np.asarray(Image.open(os.path.join(PILOT, 'bubble_riderY_clean_candidate.png')).convert('RGB')).astype(np.float64)
H, W, _ = base.shape
yy, xx = np.mgrid[0:H, 0:W]
gx, gy = xx + CX, yy + CY

def warm(p):
    r, g, b = p
    return (r > 234) & (g > 222) & (b > 205) & ((r-b) >= 5) & ((r-b) <= 48) & ((max(r,g,b)-min(r,g,b)) < 58)

def brown(p):
    r, g, b = p
    return (r < 185) & (g < 135) & (b < 118) & (r > g + 18) & (g > b + 5)

def px(a, xbg, ybg):
    return a[(gy == ybg) & (gx == xbg)][0]

def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)

# ---- warm-white row model, identical anchor bands to the published build_clean.py ----
O = orig
R, G, B = O[:,:,0], O[:,:,1], O[:,:,2]
dark = (R < 170) & (G < 125) & (B < 100) & ((R-G) > 14) & ((G-B) > 4)
warm_ok = (~dark) & (R > 232) & (G > 217) & (B > 193) & ((R-B) >= 6) & ((R-B) <= 40) & ((O.max(2)-O.min(2)) < 44)
def band_med(gy0, gy1, gx0, gx1):
    s = (gy >= gy0) & (gy <= gy1) & (gx >= gx0) & (gx <= gx1) & warm_ok
    return np.median(O[s], axis=0)
ctop = band_med(355, 365, 870, 940)
cbot = band_med(428, 434, 870, 940)
t = np.clip((gy - 360.0) / (431.0 - 360.0), 0, 1)[:, :, None]
model = ctop[None, None, :] * (1 - t) + cbot[None, None, :] * t

# ---- per-column gap + residue boundary, measured on the preserved base ----
gap = {}
for xbg in range(840, 971):
    st = next((y for y in range(420, 446) if brown(px(base, xbg, y))), None)
    gt = gb = None
    if st is not None:
        y = st - 1
        while y >= 416 and not warm(px(base, xbg, y)):
            y -= 1
        if y >= 416:
            gb = y
            while y >= 416 and warm(px(base, xbg, y)):
                y -= 1
            gt = y + 1
    gap[xbg] = {'stroke_top': st, 'gap_top': gt, 'gap_bottom': gb,
                'residue_last': (gt - 1) if gt is not None else None}

# ---- local target: row model + per-column offset measured from the clean GAP ----
col_off = np.zeros((W, 3), float)
for xbg in range(850, 961):
    g = gap[xbg]
    if g['gap_top'] is None or g['gap_bottom'] is None:
        continue
    xi = xbg - CX
    gc = (g['gap_top'] + g['gap_bottom']) / 2.0
    gap_col = base[(gx == xbg) & (gy >= g['gap_top']) & (gy <= g['gap_bottom'])]
    gap_med = np.median(gap_col, axis=0)
    model_at = ctop * (1 - np.clip((gc - 360.0) / 71.0, 0, 1)) + cbot * np.clip((gc - 360.0) / 71.0, 0, 1)
    col_off[xi] = gap_med - model_at

# Smooth the per-column offset horizontally so sampling noise cannot produce
# visible vertical stripes in the rebuilt band. Reflect-pad at the two ends.
def smooth1d(arr, radius=5):
    k = 2 * radius + 1
    ker = np.ones(k, float) / k
    pad = np.pad(arr, ((radius, radius), (0, 0)), mode='edge')
    out = np.empty_like(arr)
    for i in range(arr.shape[0]):
        out[i] = (pad[i:i+k] * ker[:, None]).sum(0)
    return out
col_off = smooth1d(col_off, radius=5)
target = model + col_off[None, :, :]

# ---- smooth alpha: rebuild only residue rows immediately above the GAP ----
alpha = np.zeros((H, W), float)
X0, X1 = 850, 960
for xbg in range(X0, X1 + 1):
    g = gap[xbg]
    rb = g['residue_last']
    if rb is None or rb < 418:
        continue
    xi = xbg - CX
    # vertical: full rebuild in the last residue rows, feathered over the rows above
    full_top = max(418, rb - 5)
    ramp_top = max(418, rb - 9)
    for ybg in range(ramp_top, rb + 1):
        yi = ybg - CY
        va = 1.0 if ybg >= full_top else smooth((ybg - ramp_top) / max(1, full_top - ramp_top))
        # horizontal feather at both ends of the arc
        ha = smooth((xbg - X0) / 4.0) * smooth((X1 - xbg) / 4.0)
        alpha[yi, xi] = max(alpha[yi, xi], va * ha)

out = (1 - alpha[:,:,None]) * base + alpha[:,:,None] * target
out = np.clip(out, 0, 255).astype(np.uint8)

rev_path = os.path.join(OUT, 'bubble_riderY_clean_rev01.png')
Image.fromarray(out).save(rev_path)

# ---- safety statistics ----
base_u = base.astype(np.uint8)
chg = np.any(out != base_u, 2)
edge = [
    int(np.abs(out[0].astype(int) - base_u[0].astype(int)).max()),
    int(np.abs(out[-1].astype(int) - base_u[-1].astype(int)).max()),
    int(np.abs(out[:,0].astype(int) - base_u[:,0].astype(int)).max()),
    int(np.abs(out[:,-1].astype(int) - base_u[:,-1].astype(int)).max()),
]
# stroke protection: compare dark-brown pixels on the strict stroke of base
brown_base = np.zeros((H, W), bool); brown_rev = np.zeros((H, W), bool)
for yi in range(H):
    for xi in range(W):
        brown_base[yi, xi] = brown(base[yi, xi].astype(int)); brown_rev[yi, xi] = brown(out[yi, xi].astype(float))
changed_bg = np.argwhere(chg)
stats = {
    'base_md5_expected': '7aa672cf51db056f664cc26790db0a7e',
    'output': os.path.basename(rev_path),
    'size': [W, H],
    'ctop': ctop.tolist(), 'cbot': cbot.tolist(),
    'changed_px_vs_base': int(chg.sum()),
    'changed_ratio_vs_base_pct': round(float(chg.mean() * 100), 3),
    'changed_bbox_crop': [int(changed_bg[:,1].min()), int(changed_bg[:,0].min()),
                          int(changed_bg[:,1].max()), int(changed_bg[:,0].max())] if len(changed_bg) else None,
    'changed_bbox_bg': [int(changed_bg[:,1].min()+CX), int(changed_bg[:,0].min()+CY),
                        int(changed_bg[:,1].max()+CX), int(changed_bg[:,0].max()+CY)] if len(changed_bg) else None,
    'four_edge_max_diff': edge,
    'stroke_pixels_base': int(brown_base.sum()),
    'stroke_pixels_rev': int(brown_rev.sum()),
    'stroke_pixels_changed_color': int(np.any(base_u[brown_base] != out[brown_base], axis=1).sum()),
    'alpha_max': float(alpha.max()),
}
with open(os.path.join(OUT, 'revision_stats.json'), 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
Image.fromarray((alpha * 255).astype(np.uint8)).save(os.path.join(OUT, 'revision_alpha.png'))
print(json.dumps(stats, ensure_ascii=False, indent=2))
