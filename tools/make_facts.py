"""Generate N1_spec_freeze/FACTS.md mechanically. Do not hand-edit its output.

Run:
    python tools/make_facts.py
"""
import hashlib
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "N1_spec_freeze", "FACTS.md")

STAGES = r"E:/un/u/My project (1)/Assets/Resources/Art/Unified_v2/food/stages"
CUTFACE = [os.path.join(STAGES, "potato_cutface.png")]
STRIPS = [os.path.join(STAGES, "potato_strip_%02d.png" % i) for i in range(1, 7)]
REFS_C = [os.path.join(HERE, "ref_cutface_ellipse.png")]
REFS_S = [os.path.join(HERE, "ref_bundle_topology.png")]
REJECTED = r"C:/Users/Administrator/WorkBuddy/cooking/_a2_committed.png"


def run(spec, files):
    files = [f for f in files if os.path.exists(f)]
    if not files:
        return "_no input files found_"
    cmd = [sys.executable, os.path.join(HERE, "asset_lint.py"), "--spec", spec] + files
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip() or r.stderr.strip()


def sha256(p):
    if not os.path.exists(p):
        return "MISSING"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = []
    L.append("# FACTS — 机器产出，请勿手改\n")
    L.append("> 本文件由 `tools/make_facts.py` 生成。每个表都附生成命令；")
    L.append("> 数字与命令不一致时，以命令重跑结果为准，不要相信本文的文本。\n")
    L.append("| 项 | 值 |\n|---|---|")
    L.append("| 生成时间 | %s |" % now)
    L.append("| Python | %s |" % platform.python_version())
    try:
        import PIL
        L.append("| Pillow | %s |" % PIL.__version__)
    except Exception:
        L.append("| Pillow | unknown |")
    L.append("| 平台 | %s |" % platform.platform())
    L.append("| 测量器 | `tools/asset_lint.py`（确定性，无随机数） |\n")

    L.append("## 表 1 — 切面（spec=cutface，阈值见 SPEC §A）\n")
    L.append("```bash\npython tools/asset_lint.py --spec cutface <A.png> <B.png>\n```\n")
    L.append(run("cutface", CUTFACE + ([REJECTED] if os.path.exists(REJECTED) else [])))
    L.append("\n")
    if os.path.exists(REJECTED):
        L.append("第 2 行为**上一轮被否决的 A-2**（1328×2112，内容铺满全画布）。")
        L.append("原图体积 2.4MB，不放入本仓库；来源与校验：\n")
        L.append("| 项 | 值 |\n|---|---|")
        L.append("| 来源 | 私有仓库 `d2f0145:ArtReview_Staging/PotatoArt_v06/CutFace_A2/potato_cutface_A2.png` |")
        L.append("| SHA256 | `%s` |\n" % sha256(REJECTED))

    L.append("## 表 2 — 现有正式丝束 6 张（spec=strip）\n")
    L.append("```bash\npython tools/asset_lint.py --spec strip potato_strip_0{1..6}.png\n```\n")
    L.append(run("strip", STRIPS))
    L.append("\n")

    L.append("## 表 3 — 参照图（证明阈值可达成，美术不可用）\n")
    L.append("```bash\npython tools/asset_lint.py --spec cutface tools/ref_cutface_ellipse.png\npython tools/asset_lint.py --spec strip tools/ref_bundle_topology.png\n```\n")
    L.append(run("cutface", REFS_C))
    L.append("\n")
    L.append(run("strip", REFS_S))
    L.append("\n")
    L.append("参照图是纯色实心 + 程序化轮廓，只用于证明「SPEC 的阈值集合存在可行解」。\n")

    L.append("## 表 4 — 文件清单与 SHA256\n")
    L.append("```bash\nsha256sum tools/*.py tools/*.png N1_spec_freeze/*.md\n```\n")
    L.append("| 文件 | 字节 | SHA256 |\n|---|---|---|")
    for p in sorted(REFS_C + REFS_S + [os.path.join(HERE, "asset_lint.py"), os.path.join(HERE, "make_facts.py")]):
        if os.path.exists(p):
            L.append("| `%s` | %d | `%s` |" % (os.path.basename(p), os.path.getsize(p), sha256(p)))
    L.append("")

    L.append("## 复现步骤\n")
    L.append("1. 取 `Assets/Resources/Art/Unified_v2/food/stages/` 下 7 个文件（1 张 cutface + 6 张 strip）；")
    L.append("2. 跑上表命令，逐字比对输出；")
    L.append("3. 若数字与本文不一致，说明素材被改过 —— 执行方需说明改动来源。\n")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("wrote", OUT, len("\n".join(L)), "chars")


if __name__ == "__main__":
    main()
