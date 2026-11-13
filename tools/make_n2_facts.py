"""Generate N2_acceptance/FACTS.md from the actual files on disk.

No number in FACTS.md is typed by a human: every table below is produced by
reading the Unity verification logs, the PNG files, spec_v8.json and git.
Run `python tools/make_n2_facts.py <section>` to print any single table, or
`python tools/make_n2_facts.py` to rewrite the whole FACTS.md.

The input files live in a PRIVATE Unity repository, so a reviewer who only
has this public repository can read the commands and the input hashes but
cannot re-run them. That limitation is disclosed in N2 README, claim C5.
"""
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = Path("E:/un/u/My project (1)")
STAGE = REPO / "ArtReview_Staging"
V7 = STAGE / "GreenPepper_v07"
V8 = STAGE / "GreenPepper_v08"
OFFICIAL = REPO / "Assets/Resources/Art/Unified_v2/food/stages"
TMP = Path("C:/Users/Administrator/WorkBuddy/cooking")
HAND = "green_pepper_prep_hand.png"
OUT = ROOT / "N2_acceptance" / "FACTS.md"
SECTIONS = ["verify", "live", "sprites", "hand", "git", "inputs"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")


def pngs(d):
    return sorted(p.name for p in Path(d).glob("*.png"))


def git(*args):
    return subprocess.run(["git", "-C", str(REPO)] + list(args),
                          capture_output=True, text=True).stdout.strip()


def label(p):
    p = Path(p)
    return "%s/%s" % (p.parent.name, p.name)


def banner(title, cmd, inputs):
    s = "\n## %s\n\n```bash\n%s\n```\n\n" % (title, cmd)
    s += "输入 SHA256（前 12 位）： " + "， ".join(
        "`%s`=%s" % (label(p), sha(p)[:12]) for p in inputs) + "\n\n"
    return s


def cmd(sec):
    return "python tools/make_n2_facts.py %s" % sec


def sec_verify():
    p = TMP / "s12_verify.log"
    t = read(p)
    full = re.search(r"FULLRECT (\d+)/(\d+) missing=(\d+)", t)
    load = re.search(r"S11 CHANGED SPRITES (\d+)/(\d+)", t)
    st = re.search(r"lines=(\d+) PASS=(\d+) FAIL=(\d+)", t)
    consoles = re.findall(r"Retrieved (\d+) log entries", t)
    state = re.search(r"compiling=(\w+) playing=(\w+)", t)
    rows = [
        ("控制台日志条数（逐次读取）", ",".join(consoles) or "n/a", "全部为 0"),
        ("Unity 编辑态", "%s / %s" % (state.group(1), state.group(2))
         if state else "n/a", "compiling=False playing=False"),
        ("FULLRECT", "/".join(full.groups()[:2]) if full else "n/a", "33/33"),
        ("missing", full.group(3) if full else "n/a", "0"),
        ("S11 CHANGED SPRITES 可加载", "/".join(load.groups())
         if load else "n/a", "12/12"),
        ("DevSelfTest lines", st.group(1) if st else "n/a", "300"),
        ("DevSelfTest PASS", st.group(2) if st else "n/a", "300"),
        ("DevSelfTest FAIL", st.group(3) if st else "n/a", "0"),
    ]
    s = banner("表 1 — 编译 / 探针 / 自测（脚本读日志原文）",
               cmd("verify"), [p, HERE / "make_n2_facts.py"])
    s += "| 项 | 实测 | SPEC 期望 |\n|---|---|---|\n"
    s += "".join("| %s | %s | %s |\n" % r for r in rows)
    return s


def sec_live():
    p = TMP / "s12_live.log"
    t = read(p)
    caps = re.findall(r"^\[(cap_[\w]+)\s*\]", t, re.M)
    sheets = sorted(set(re.findall(r"sheetNow=(green_pepper_sheet_\d)", t)))
    shots = len(list((REPO / "_wbshots/s12").glob("*.png")))
    before = len(list((REPO / "_wbshots/s12_before").glob("*.png")))
    rows = [
        ("实机日志 cap_ 帧数", str(len(caps))),
        ("whiteFlash=False 出现次数", str(t.count("whiteFlash=False"))),
        ("sheetMode=True 出现次数", str(t.count("sheetMode=True"))),
        ("sheetNow 分段帧集合", ",".join(s.replace("green_pepper_sheet_", "")
                                  for s in sheets) or "n/a"),
        ("stripsOn=8 出现", str("stripsOn=8" in t)),
        ("末帧入备料位", str("target=green_pepper_slice/Ready" in t)),
        ("_wbshots/s12/*.png", str(shots)),
        ("_wbshots/s12_before/*.png", str(before)),
    ]
    s = banner("表 2 — 干净 Play Mode 实机日志与截图计数",
               cmd("live"), [p, HERE / "make_n2_facts.py"])
    s += "| 项 | 实测 |\n|---|---|\n"
    s += "".join("| %s | %s |\n" % r for r in rows)
    return s


def sec_sprites():
    v8, v7 = pngs(V8), pngs(V7)
    changed = [n for n in v8 if sha(V8 / n) != sha(V7 / n)]
    mismatch = [n for n in v8
                if (OFFICIAL / n).exists()
                and sha(V8 / n) != sha(OFFICIAL / n)]
    spec = json.loads(read(V8 / "spec_v8.json"))
    spec_bad = [n for n, i in spec["files"].items()
                if sha(V8 / n) != i["sha256"]]
    base = json.loads(read(TMP / "_s12_v7_baseline.json"))
    v7diff = [n for n in base if sha(V7 / n) != base[n]]
    official = sorted(p.name for p in OFFICIAL.glob("green_pepper_*.png"))
    digest = hashlib.sha256(
        "".join(sha(V8 / n) for n in v8).encode()).hexdigest()
    rows = [
        ("v08 PNG 数", len(v8), "33"),
        ("v07 PNG 数", len(v7), "33"),
        ("v08 vs v07 变化集合", ",".join(changed) or "(空)", "仅 " + HAND),
        ("正式 stages 青椒 PNG 数", len(official), "32"),
        ("v08 vs 正式 stages SHA 不一致", ",".join(mismatch) or "(空)", "(空)"),
        ("spec_v8.json 条目", len(spec["files"]), "33"),
        ("spec_v8.json SHA 不匹配", ",".join(spec_bad) or "(空)", "(空)"),
        ("v07 37 文件基线变化", ",".join(v7diff) or "(空)", "(空)"),
        ("v08 33 张 SHA 串接摘要", digest[:16] + "…", "可复算"),
    ]
    s = banner("表 3 — 素材字节一致性（逐张 SHA256）",
               cmd("sprites"), [V8 / "spec_v8.json", V8 / HAND,
                                V7 / HAND, TMP / "_s12_v7_baseline.json"])
    s += "| 项 | 实测 | SPEC 期望 |\n|---|---|---|\n"
    s += "".join("| %s | %s | %s |\n" % r for r in rows)
    return s


def hand_stats(p):
    a = np.array(Image.open(p).convert("RGBA"))
    R, G, B, A = [a[..., i].astype(np.int16) for i in range(4)]
    skin = ((R > 195) & (G > 130) & (G < 215) & (B > 105) & (B < 200)
            & (A > 120) & (R > G + 25))
    ys, xs = np.nonzero(skin)
    ay, ax = np.nonzero(A > 20)
    return {
        "alphaBBox": [int(ax.min()), int(ay.min()), int(ax.max()), int(ay.max())],
        "skinBBox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "centroid": [int(round(xs.mean())), int(round(ys.mean()))],
    }, a


def sec_hand():
    l, la = hand_stats(V7 / HAND)
    r, ra = hand_stats(V8 / HAND)
    mirror = bool(np.array_equal(ra, la[:, ::-1, :]))
    rows = [
        ("v07 肤色重心 (x,y)", str(l["centroid"]), "593,511"),
        ("v08 肤色重心 (x,y)", str(r["centroid"]), "430,511"),
        ("v07 alpha bbox min/max（含端点）", str(l["alphaBBox"]), "—"),
        ("v08 alpha bbox min/max（含端点）", str(r["alphaBBox"]), "—"),
        ("v07 alpha bbox 半开 [x0,y0,x1,y1)", str([l["alphaBBox"][0],
                                                   l["alphaBBox"][1],
                                                   l["alphaBBox"][2] + 1,
                                                   l["alphaBBox"][3] + 1]), "—"),
        ("v08 alpha bbox 半开 [x0,y0,x1,y1)", str([r["alphaBBox"][0],
                                                   r["alphaBBox"][1],
                                                   r["alphaBBox"][2] + 1,
                                                   r["alphaBBox"][3] + 1]), "—"),
        ("v08 == v07 水平镜像（逐像素）", str(mirror), "True"),
        ("抓握 y 是否等于主体中点", str(l["centroid"][1] == r["centroid"][1] == 511), "True"),
    ]
    s = banner("表 4 — 手部几何（PIL + numpy 实测；alpha>20，肤色阈值见脚本）",
               cmd("hand"), [V7 / HAND, V8 / HAND])
    s += "| 项 | 实测 | 期望 |\n|---|---|---|\n"
    s += "".join("| %s | %s | %s |\n" % x for x in rows)
    s += ("\n> 口径：`S12_report.md` / `spec_v8.json.handFraming` 用**半开** bbox，"
          "上面前两行是含端点的 min/max，两者相差 1px，不是矛盾。"
          "`spec_v8.json.files[].bbox` 则是第三种口径 `[x,y,宽,高]`（alpha>8），不可混用。\n")
    return s


def sec_git():
    head = git("log", "-1", "--format=%h %s")
    branch = git("branch", "--show-current")
    status = git("status", "--short").splitlines()
    staged = git("diff", "--cached", "--name-only").splitlines()
    prot = [
        REPO / "Assets/Resources/Art/Unified_v2/food/stages/potato_base_1024.png",
        REPO / "Assets/Resources/Art/Unified_v2/food/food_raw_beef.png",
    ]
    rows = [
        ("HEAD", head or "(git 不可用)", "以 d2f0145 开头"),
        ("branch", branch or "(git 不可用)", "refactor/data-driven-food"),
        ("git status --short 行数", str(len(status)), ">0（未提交）"),
        ("已暂存文件数", str(len(staged)), "0"),
    ] + [("%s mtime" % p.name,
          datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
          "2026-11-01 16:53") for p in prot if p.exists()]
    s = banner("表 5 — 工程保护状态（直接跑 git / stat）",
               cmd("git"), [HERE / "make_n2_facts.py"])
    s += "| 项 | 实测 | 期望 |\n|---|---|---|\n"
    s += "".join("| %s | %s | %s |\n" % x for x in rows)
    return s


def sec_inputs():
    files = [
        HERE / "make_n2_facts.py",
        TMP / "s12_verify.log", TMP / "s12_live.log",
        V8 / "spec_v8.json", V8 / HAND, V7 / HAND,
        TMP / "_s12_v7_baseline.json",
        TMP / "S12_report.md", TMP / "S12_spec.md",
    ]
    s = banner("表 6 — 输入文件清单与 SHA256（复算入口）",
               cmd("inputs"), [HERE / "make_n2_facts.py"])
    s += "| 文件 | 字节 | SHA256 |\n|---|---|---|\n"
    s += "".join("| `%s` | %d | `%s` |\n" %
                 (label(p), p.stat().st_size, sha(p)) for p in files)
    return s


SECFN = {k: globals()["sec_" + k] for k in SECTIONS}


def main():
    sec = sys.argv[1] if len(sys.argv) > 1 else "all"
    if sec != "all" and sec not in SECFN:
        sys.exit("usage: make_n2_facts.py [all|%s]" % "|".join(SECTIONS))
    if sec != "all":
        print(SECFN[sec]().strip())
        return
    head = ("# FACTS — 机器产出，请勿手改\n\n"
            "> 本文件由 `tools/make_n2_facts.py` 生成；每个表附生成命令与输入 SHA256。\n"
            "> 数字与命令重跑结果不一致时，以重跑结果为准，不要相信本文文本。\n\n"
            "| 项 | 值 |\n|---|---|\n"
            "| 生成时间(UTC) | %s |\n"
            "| Python | %s |\n"
            "| 平台 | %s |\n"
            "| 生成脚本 SHA256 | `%s` |\n"
            "| 节点 | N2 产出验收：青椒 S7–S12 / v08 |\n"
            % (datetime.datetime.now(datetime.timezone.utc)
               .strftime("%Y-%m-%d %H:%M:%S UTC"),
               platform.python_version(), platform.platform(), sha(__file__)))
    body = "".join(SECFN[k]() for k in SECTIONS)
    tail = ("\n## 复现步骤与边界\n\n"
            "```bash\ncd <public-review-repo>\n"
            "python tools/make_n2_facts.py            # 重写 FACTS.md\n"
            "python tools/make_n2_facts.py verify     # 只打印表 1\n"
            "```\n\n"
            "| 边界 | 说明 |\n|---|---|\n"
            "| 输入位置 | 表 1–5 的输入全部在**私有 Unity 仓库**与工程外暂存目录，"
            "公开仓库只有脚本与哈希 |\n"
            "| 评审方可复现性 | **不能独立重跑**，只能核对命令、输入 SHA256 与逻辑自洽；"
            "见 N2 README 主张 C5 |\n"
            "| 图片 | 本节点零图片；表 4 的数字来自对 PNG 像素的脚本测量，"
            "不是对图片的主观描述 |\n")
    text = head + body + tail
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT, "lines", len(text.splitlines()))


if __name__ == "__main__":
    main()
