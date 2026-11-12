"""asset_lint.py - describe a PNG sprite in numbers, so a text-only reviewer can judge it.

Usage:
    python asset_lint.py <png> [<png> ...]
    python asset_lint.py --spec cutface|strip <png> [...]

Output: one markdown row per file. All metrics are deterministic (no randomness).

Metrics:
  canvas        WxH
  bbox          alpha bounding box (x,y,w,h)
  opaque        opaque pixel ratio inside bbox
  waist         min thickness in middle 30-70% / max thickness   (1.0 = no waist)
  waistPos      where the waist sits along the long axis (0-1)
  taperEnd      mean thickness at the outer 4% of both ends / max (1.0 = blunt)
  straight      longest run of near-max-thickness slices / total  (1.0 = pure rectangle)
  edgeLum       darkest luminance among pixels within 6px of the alpha edge (low = heavy outline)
  colors        top-3 quantised colours inside the shape
  verdict       PASS/FAIL against the requested spec
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

SPECS = {
    "cutface": {
        "canvas": (1024, 1024),
        "bbox": (464, 46, 96, 819),
        "bbox_tol": 2,
        "max_straight": 0.55,
        "max_end_taper": 0.55,
        "min_edge_lum": 150,
        "require_waist": False,
    },
    "strip": {
        "canvas": (512, 512),
        "bbox_w": (240, 300),
        "bbox_h": (105, 145),
        "min_waist_drop": 0.30,
        "max_taper_end": 0.30,
        "min_edge_lum": 120,
        "min_solidity": 0.88,
        "min_compact": 0.30,
    },
}


def load(path):
    im = Image.open(path).convert("RGBA")
    return np.array(im), im.size


def _hull_area(xs, ys):
    """Convex hull area via monotone chain (pure numpy, no scipy)."""
    pts = sorted(set(zip(xs.tolist(), ys.tolist())))
    if len(pts) < 3:
        return 0.0

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    s = 0.0
    for i in range(len(hull)):
        x1, y1 = hull[i]
        x2, y2 = hull[(i + 1) % len(hull)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def measure(arr):
    a = arr[..., 3]
    mask = a > 8
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    x0, y0 = int(xs.min()), int(ys.min())
    w, h = int(xs.max() - x0 + 1), int(ys.max() - y0 + 1)
    crop = mask[y0:y0 + h, x0:x0 + w]
    opaque = float(crop.mean())

    horizontal = w >= h
    prof = crop.sum(axis=0) if horizontal else crop.sum(axis=1)
    n = len(prof)
    max_t = float(prof.max()) or 1.0

    mid = prof[int(n * 0.30):int(n * 0.70)]
    if len(mid) == 0:
        mid = prof
    waist = float(mid.min()) / max_t
    waist_pos = (int(n * 0.30) + int(np.argmin(mid))) / n

    tail = max(3, int(round(n * 0.04)))
    ends = np.concatenate([prof[:tail], prof[-tail:]])
    taper_end = float(ends.mean()) / max_t

    # monotonic taper: walking from the thickest slice to either end,
    # what fraction of steps never increase? scattered lines bounce up and down.
    peak = int(np.argmax(prof))
    segs = []
    if peak >= 2:
        segs.append(prof[:peak + 1][::-1])
    if n - peak >= 3:
        segs.append(prof[peak:])
    dec = tot = 0
    for s in segs:
        d = np.diff(s.astype(float))
        dec += int((d <= max_t * 0.04).sum())
        tot += len(d)
    mono = dec / tot if tot else 0.0

    ys2, xs2 = np.nonzero(crop)
    st = max(1, int(np.sqrt(len(xs2)) / 80))
    hull = _hull_area(xs2[::st], ys2[::st])
    solidity = float(crop.sum()) / hull if hull > 0 else 0.0

    # shape factor 4*pi*A/P^2: ragged (many separate strands) -> very low, smooth bundle -> high.
    # pad by 1px False so the bbox-adjacent boundary is counted, otherwise P is ~half the truth.
    pad = np.pad(crop, 1, constant_values=False)
    per = int((pad[1:, :] ^ pad[:-1, :]).sum() + (pad[:, 1:] ^ pad[:, :-1]).sum())
    area = float(crop.sum())
    compact = 4.0 * np.pi * area / (per * per) if per else 0.0

    near_max = np.abs(prof - max_t) <= max_t * 0.05
    best = run = 0
    for v in near_max:
        run = run + 1 if v else 0
        best = max(best, run)
    straight = best / n

    lum = arr[..., :3].mean(axis=2)
    solid = a > 200
    # 6px erosion via MinFilter (odd size 13) - same as binary erosion for a 0/255 mask
    inner = np.array(Image.fromarray((solid * 255).astype(np.uint8)).filter(
        ImageFilter.MinFilter(13))) > 127
    edge = solid & ~inner
    edge_lum = float(lum[edge].min()) if edge.any() else 255.0

    px = arr[..., :3][mask]
    q = (px // 16 * 16).astype(np.uint8)
    vals, counts = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    order = np.argsort(-counts)[:3]
    colors = ["#%02X%02X%02X" % tuple(vals[i]) for i in order]

    return dict(bbox=(x0, y0, w, h), opaque=opaque, waist=waist, waist_pos=waist_pos,
                taper_end=taper_end, mono=mono, solidity=solidity, compact=compact,
                straight=straight, edge_lum=edge_lum, colors=colors)


def verdict(m, size, spec_name):
    if not spec_name:
        return "-"
    s = SPECS[spec_name]
    fails = []
    if "canvas" in s and tuple(size) != s["canvas"]:
        fails.append("canvas")
    if "bbox" in s:
        exp = s["bbox"]
        if any(abs(a - b) > s["bbox_tol"] for a, b in zip(m["bbox"], exp)):
            fails.append("bbox")
    if "bbox_w" in s:
        lo, hi = s["bbox_w"]
        if not (lo <= m["bbox"][2] <= hi):
            fails.append("bbox_w")
        lo, hi = s["bbox_h"]
        if not (lo <= m["bbox"][3] <= hi):
            fails.append("bbox_h")
    if "max_straight" in s and m["straight"] > s["max_straight"]:
        fails.append("straight")
    if "max_end_taper" in s and m["taper_end"] > s["max_end_taper"]:
        fails.append("blunt_ends")
    if "min_waist_drop" in s and (1.0 - m["waist"]) < s["min_waist_drop"]:
        fails.append("no_waist")
    if "max_taper_end" in s and m["taper_end"] > s["max_taper_end"]:
        fails.append("blunt_ends")
    if "min_solidity" in s and m["solidity"] < s["min_solidity"]:
        fails.append("loose_silhouette")
    if "min_compact" in s and m["compact"] < s["min_compact"]:
        fails.append("ragged_edge")
    if "min_edge_lum" in s and m["edge_lum"] < s["min_edge_lum"]:
        fails.append("dark_outline")
    return "PASS" if not fails else "FAIL:" + ",".join(fails)


def main(argv):
    spec_name = None
    args = []
    i = 0
    while i < len(argv):
        if argv[i] == "--spec":
            i += 1
            spec_name = argv[i]
        else:
            args.append(argv[i])
        i += 1

    print("| file | canvas | bbox | opaque | waist | waistPos | endTaper | solidity | compact | straight | edgeLum | colors | verdict |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for p in args:
        arr, size = load(p)
        m = measure(arr)
        name = p.replace("\\", "/").split("/")[-1]
        if m is None:
            print("| %s | %dx%d | empty | - | - | - | - | - | - | - | - | - | - |" % (name, size[0], size[1]))
            continue
        print("| %s | %dx%d | %d,%d,%d,%d | %.3f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %.0f | %s | %s |" % (
            name, size[0], size[1],
            m["bbox"][0], m["bbox"][1], m["bbox"][2], m["bbox"][3],
            m["opaque"], m["waist"], m["waist_pos"], m["taper_end"], m["solidity"], m["compact"],
            m["straight"], m["edge_lum"], " ".join(m["colors"]),
            verdict(m, size, spec_name)))


if __name__ == "__main__":
    main(sys.argv[1:])
