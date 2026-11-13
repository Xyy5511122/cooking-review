"""Generate N2_acceptance/FACTS.md from the actual files on disk.

No number in FACTS.md is typed by a human: every table below is produced by
reading the Unity verification logs, the PNG files, the two spec JSONs and git.
Run `python tools/make_n2_facts.py <section>` to print any single table, or
`python tools/make_n2_facts.py` to rewrite the whole FACTS.md.

v2 (CONDITIONAL revision):
  * Two pure-text logs are published in N2_acceptance/evidence/, so a reviewer
    who only has this public repository CAN independently re-run `verify` and
    `live` (tables 1-2). The script prefers that public copy.
  * Tables 7-9 were added in response to review items [2], [3], [4]:
    S12 change set vs the pre-stage snapshot, material-layer visibility proxy
    measurements, and the actual sign-off field values.
  * Tables 1-6 measured values are unchanged; only the generator hash changes.

Tables 3-9 still need inputs from the PRIVATE Unity repository. The script
refuses to overwrite FACTS.md when those inputs are absent.
"""
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from collections import Counter
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
BACKUP = TMP / "_S12_backup"
EVIDENCE = ROOT / "N2_acceptance" / "evidence"
HAND = "green_pepper_prep_hand.png"
OUT = ROOT / "N2_acceptance" / "FACTS.md"
SECTIONS = ["verify", "live", "sprites", "hand", "git", "inputs",
            "changes", "visibility", "signoff"]

BACKUP_MAP = {
    "DevSelfTest.cs": "Assets/Scripts/CookingDemo/DevSelfTest.cs",
    "FoodShredding.cs": "Assets/Scripts/CookingDemo/FoodShredding.cs",
    "FoodVisual.cs": "Assets/Scripts/CookingDemo/FoodVisual.cs",
    "PrepChoreography.cs": "Assets/Scripts/CookingDemo/PrepChoreography.cs",
    "PrepStepsController.cs": "Assets/Scripts/CookingDemo/PrepStepsController.cs",
    "ShredProfile.cs": "Assets/Scripts/CookingDemo/ShredProfile.cs",
    "choreography_green_pepper.asset":
        "Assets/Resources/PrepChoreography/green_pepper.asset",
    "shredprofile_green_pepper.asset":
        "Assets/Resources/ShredProfiles/green_pepper.asset",
    "food_green_pepper_slice.png":
        "Assets/Resources/Art/Unified_v2/food/food_green_pepper_slice.png",
}

VIS_FILES = [
    "green_pepper_prep_whole.png",
    "green_pepper_prep_headless.png",
    "green_pepper_prep_no_butt.png",
    "green_pepper_prep_head_piece.png",
    "green_pepper_prep_butt_piece.png",
]


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
    if p.parent.name == "stages":
        return "%s/stages/%s" % (p.parent.parent.name, p.name)
    return "%s/%s" % (p.parent.name, p.name)


def banner(title, cmd, inputs):
    s = "\n## %s\n\n```bash\n%s\n```\n\n" % (title, cmd)
    s += "输入 SHA256（前 12 位）： " + "， ".join(
        "`%s`=%s" % (label(p), sha(p)[:12]) for p in inputs) + "\n\n"
    return s


def cmd(sec):
    return "python tools/make_n2_facts.py %s" % sec


def public_log(name):
    """Prefer the published byte-identical copy, so table 1/2 can be re-run
    by a reviewer who only has this public repository."""
    p = EVIDENCE / name
    return p if p.exists() else TMP / name


def private_ok():
    # Allows anyone to verify the "cannot re-run" boundary on a machine that
    # happens to have the private paths: N2_PUBLIC_ONLY=1 simulates a reviewer.
    if os.environ.get("N2_PUBLIC_ONLY") == "1":
        return False
    return REPO.exists() and TMP.exists() and (V8 / "spec_v8.json").exists()


def sec_verify():
    p = public_log("s12_verify.log")
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
    s = banner("表 1 — 编译 / 探针 / 自测（脚本读日志原文；日志已公开）",
               cmd("verify"), [p, HERE / "make_n2_facts.py"])
    s += "| 项 | 实测 | SPEC 期望 |\n|---|---|---|\n"
    s += "".join("| %s | %s | %s |\n" % r for r in rows)
    return s


def sec_live():
    p = public_log("s12_live.log")
    t = read(p)
    caps = re.findall(r"^\[(cap_[\w]+)\s*\]", t, re.M)
    sheets = sorted(set(re.findall(r"sheetNow=(green_pepper_sheet_\d)", t)))
    rows = [
        ("实机日志 cap_ 帧数", str(len(caps))),
        ("whiteFlash=False 出现次数", str(t.count("whiteFlash=False"))),
        ("sheetMode=True 出现次数", str(t.count("sheetMode=True"))),
        ("sheetNow 分段帧集合", ",".join(s.replace("green_pepper_sheet_", "")
                                  for s in sheets) or "n/a"),
        ("stripsOn=8 出现", str("stripsOn=8" in t)),
        ("末帧入备料位", str("target=green_pepper_slice/Ready" in t)),
    ]
    s = banner("表 2 — 干净 Play Mode 实机日志（纯公开输入，可独立重跑）",
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


def _backup_current(rel):
    if rel.startswith("stages/"):
        return OFFICIAL / Path(rel).name
    if rel.startswith("review_v07/"):
        return V7 / Path(rel).name
    return REPO / BACKUP_MAP[rel]


def sec_changes():
    """[2] Prove the S12 change set for ALL file types, not just PNG."""
    bfiles = sorted(p for p in BACKUP.rglob("*") if p.is_file())
    changed = []
    kinds = Counter()
    for p in bfiles:
        rel = p.relative_to(BACKUP).as_posix()
        kinds[Path(rel).suffix.lstrip(".")] += 1
        cur = _backup_current(rel)
        if not cur.exists() or sha(p) != sha(cur):
            changed.append(rel)
    changed_kinds = Counter(Path(r).suffix.lstrip(".") for r in changed)
    start = BACKUP.stat().st_mtime
    late = [p for p in (REPO / "Assets").rglob("*")
            if p.is_file() and p.stat().st_mtime > start + 2]
    late_code = [p for p in late if p.suffix in (".cs", ".asset", ".meta")]
    st = git("status", "--short").splitlines()
    head_kinds = Counter(Path(line[3:].strip().strip('"')).suffix.lstrip(".")
                         for line in st if len(line) > 3)
    rows = [
        ("S12 起点快照文件数", len(bfiles), "快照规模"),
        ("快照逐文件 SHA 变化集合", ",".join(changed) or "(空)", "回答评审 [2]"),
        ("快照中 C# 文件数 / 变化数", "%d / %d" %
         (kinds["cs"], changed_kinds["cs"]), "覆盖 6 个切配 C#"),
        ("快照中 .asset 文件数 / 变化数", "%d / %d" %
         (kinds["asset"], changed_kinds["asset"]), "覆盖 2 个青椒资产"),
        ("快照中 PNG 文件数 / 变化数", "%d / %d" %
         (kinds["png"], changed_kinds["png"]), "33 张青椒 PNG"),
        ("快照中 v07 review 文本数 / 变化数", "%d / %d" %
         (kinds["md"] + kinds["json"],
          changed_kinds["md"] + changed_kinds["json"]), "历史验收快照"),
        ("S12 起点时刻", datetime.datetime.fromtimestamp(start)
         .strftime("%Y-%m-%d %H:%M:%S"), "mtime 扫描基线"),
        ("Assets/ 下 mtime 晚于起点的文件", ",".join(
            p.relative_to(REPO / "Assets").as_posix() for p in late) or "(空)",
         "全目录扫描，含 .meta"),
        ("其中 .cs / .asset / .meta 数", len(late_code), "回答评审 [2]"),
        ("相对 HEAD 的 git status 行数（历史遗留，口径不同）", len(st),
         "不用于 S12 判定"),
        ("相对 HEAD 的 cs/asset/meta 计数（累计未提交）", "%d/%d/%d" %
         (head_kinds["cs"], head_kinds["asset"], head_kinds["meta"]),
         "不用于 S12 判定"),
    ]
    s = banner("表 7 — S12 变更集合（起点快照 45 文件逐 SHA + 全 Assets mtime 扫描）",
               cmd("changes"), [BACKUP / "stages" / HAND,
                                OFFICIAL / HAND,
                                REPO / "Assets/Scripts/CookingDemo/PrepStepsController.cs",
                                REPO / "Assets/Resources/PrepChoreography/green_pepper.asset"])
    s += "| 项 | 实测 | 说明（**非期望值，不产生判定**） |\n|---|---|---|\n"
    s += "".join("| %s | %s | %s |\n" % r for r in rows)
    s += ("\n> 口径：`_S12_backup/` 是 S12 动手前的 45 文件快照；"
          "「变化」= 与该快照逐文件 SHA256 不一致。`git status` 是**相对 HEAD "
          "d2f0145 的累计未提交改动**（含 S7–S11 遗留），不能拿来证明或否定 S12 本轮改动。"
          "`.meta` 不在快照内，用 Assets/ 全量 mtime 扫描补足。"
          "**本表只补证据，N2-01..16 的期望值与判定方式不变。**\n")
    return s


def _rgba(p):
    return np.array(Image.open(p).convert("RGBA"))


def sec_visibility():
    """[3] Material-layer visibility proxy. NOT a claim about human vision."""
    cut = json.loads(read(V7 / "spec_v7.json"))["cutY"]
    hy, by = int(cut["head"]), int(cut["butt"])
    top_win = (hy - 8, hy + 60)
    bot_win = (by - 50, by + 10)
    hand = _rgba(V8 / HAND)[..., 3] > 20
    art = {n: _rgba(V8 / n) for n in VIS_FILES}

    def alpha_mask(n):
        return art[n][..., 3] > 20

    def pale_mask(n):
        a = art[n]
        R, G, B, A = [a[..., i].astype(np.int16) for i in range(4)]
        return ((R > 165) & (G > 185) & (B > 110) & (A > 120)
                & (G > R - 10) & alpha_mask(n))

    def pair(mask, y0=None, y1=None):
        m = mask.copy()
        if y0 is not None:
            m[:y0] = False
            m[y1:] = False
        total = int(m.sum())
        free = int((m & ~hand).sum())
        return "%d / %d" % (total, free)

    rows = [
        ("手层 alpha>20 覆盖像素数", int(hand.sum()), "遮挡基准"),
        ("整椒顶部 y<%d（果梗/头顶）alpha / 未被手遮挡" % hy,
         pair(alpha_mask("green_pepper_prep_whole.png"), 0, hy), "回答评审 [3]"),
        ("整椒底部 y>%d（圆底）alpha / 未被手遮挡" % by,
         pair(alpha_mask("green_pepper_prep_whole.png"), by, 1024), "回答评审 [3]"),
        ("上切口带 y=%d..%d 的浅内壁像素 / 未被遮挡（headless）" % top_win,
         pair(pale_mask("green_pepper_prep_headless.png"), *top_win), "回答评审 [3]"),
        ("上切口带 y=%d..%d 的浅内壁像素 / 未被遮挡（no_butt）" % top_win,
         pair(pale_mask("green_pepper_prep_no_butt.png"), *top_win), "回答评审 [3]"),
        ("下切口带 y=%d..%d 的浅内壁像素 / 未被遮挡（no_butt）" % bot_win,
         pair(pale_mask("green_pepper_prep_no_butt.png"), *bot_win), "回答评审 [3]"),
        ("同窗口对照（headless，尚未切尾）",
         pair(pale_mask("green_pepper_prep_headless.png"), *bot_win), "状态差异对照"),
        ("椒头落料 alpha / 未被手遮挡",
         pair(alpha_mask("green_pepper_prep_head_piece.png")), "回答评审 [3]"),
        ("底片环落料 alpha / 未被手遮挡",
         pair(alpha_mask("green_pepper_prep_butt_piece.png")), "回答评审 [3]"),
    ]
    s = banner("表 8 — 素材层可见性代理量（alpha>20；浅内壁阈值沿用 S11）",
               cmd("visibility"), [V7 / "spec_v7.json", V8 / HAND] +
               [V8 / n for n in VIS_FILES])
    s += ("| 项 | 实测（总像素 / 未被手层遮挡） | "
          "说明（**非期望值，不产生判定**） |\n|---|---|---|\n")
    s += "".join("| %s | %s | %s |\n" % r for r in rows)
    s += ("\n> 口径：切口窗口由 `spec_v7.json.cutY`（head=%d / butt=%d）派生；"
          "浅内壁阈值是 S11 报告的复算参数，**不是验收阈值**。这些数字只证明"
          "素材层存在未被手图层遮挡的像素，**不证明 UGUI 实际渲染可见、"
          "不证明用户视觉上可见**；实机呈现由用户目视验收。"
          "**本表只补证据，不新增判定条款。**\n" % (hy, by))
    return s


def sec_signoff():
    """[4] Actual sign-off field values, plus the spec_v7.json input hash."""
    v7 = json.loads(read(V7 / "spec_v7.json"))
    v8 = json.loads(read(V8 / "spec_v8.json"))
    a7, a8, s12 = v7["acceptance"], v8["acceptance"], v8["s12Acceptance"]
    rows = [
        ("spec_v7.json SHA256（完整）", sha(V7 / "spec_v7.json"),
         "评审 [4] 要求的输入哈希"),
        ("spec_v8.json SHA256（完整）", sha(V8 / "spec_v8.json"), "输入哈希"),
        ("spec_v7.json.acceptance.signedOffBy", a7["signedOffBy"], "字段原值"),
        ("spec_v7.json.acceptance.signedOffAt", a7["signedOffAt"], "第一次签核"),
        ("spec_v7.json.acceptance.closedRequirements",
         ",".join(a7["closedRequirements"]), "第一次关闭的需求"),
        ("spec_v8.json.acceptance.signedOffAt（v07 历史副本）",
         a8["signedOffAt"], "与 v07 相同，非第三次签核"),
        ("spec_v8.json.s12Acceptance.signedOffBy", s12["signedOffBy"], "字段原值"),
        ("spec_v8.json.s12Acceptance.signedOffAt", s12["signedOffAt"], "第二次签核"),
        ("spec_v8.json.s12Acceptance.closedRequirements",
         ",".join(s12["closedRequirements"]), "第二次关闭的需求"),
        ("v08.acceptance == v07.acceptance（说明是副本，非第三次签核）",
         str(a8 == a7), "字段等值比较"),
        ("两次签核时间不同", str(a7["signedOffAt"] != s12["signedOffAt"]),
         "独立登记核对"),
        ("两次关闭需求集合不相交", str(not set(a7["closedRequirements"])
                                     & set(s12["closedRequirements"])),
         "独立登记核对"),
        ("v07 status 字段前缀", v7["status"].split(".")[0], "ACCEPTED / frozen"),
        ("v08 status 字段前缀", v8["status"].split(".")[0], "ACCEPTED / frozen"),
    ]
    s = banner("表 9 — 两次签核字段实际值与 spec 输入哈希",
               cmd("signoff"), [V7 / "spec_v7.json", V8 / "spec_v8.json"])
    s += ("| 项 | 实测 | 说明（**非期望值，不产生判定**） |\n|---|---|---|\n")
    s += "".join("| %s | %s | %s |\n" % r for r in rows)
    s += ("\n> 口径：`spec_v8.json` 内同时含 `acceptance`（v07 签核副本）与 "
          "`s12Acceptance`（第二次签核）；两者时间不同、关闭需求不相交。"
          "**本表只补证据，不新增判定条款。**\n")
    return s


def sec_inputs():
    files = [
        HERE / "make_n2_facts.py",
        EVIDENCE / "s12_verify.log", EVIDENCE / "s12_live.log",
        V8 / "spec_v8.json", V7 / "spec_v7.json",
        V8 / HAND, V7 / HAND,
    ] + [V8 / n for n in VIS_FILES] + [
        TMP / "_s12_v7_baseline.json",
        BACKUP / "stages" / HAND,
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
    if sec not in ("verify", "live") and not private_ok():
        sys.exit("private Unity inputs unavailable: section '%s' cannot run. "
                 "FACTS.md was NOT overwritten. Public-only sections: "
                 "verify, live." % sec)
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
            "| 对应 SPEC 版本 | v2（CONDITIONAL 修订） |\n"
            "| 节点 | N2 产出验收：青椒 S7–S12 / v08 |\n"
            % (datetime.datetime.now(datetime.timezone.utc)
               .strftime("%Y-%m-%d %H:%M:%S UTC"),
               platform.python_version(), platform.platform(), sha(__file__)))
    body = "".join(SECFN[k]() for k in SECTIONS)
    tail = ("\n## 复现步骤与边界\n\n"
            "```bash\ncd <public-review-repo>\n"
            "python tools/make_n2_facts.py verify   # 表 1：公开日志，可独立重跑\n"
            "python tools/make_n2_facts.py live     # 表 2：公开日志，可独立重跑\n"
            "python tools/make_n2_facts.py changes  # 表 7：需要私有工程，公开环境会拒绝\n"
            "N2_PUBLIC_ONLY=1 python tools/make_n2_facts.py changes  # 演示拒绝边界\n"
            "python tools/make_n2_facts.py          # 全表重写（仅执行方）\n"
            "```\n\n"
            "| 边界 | 说明 |\n|---|---|\n"
            "| 表 1 / 表 2 输入 | `N2_acceptance/evidence/` 两份纯文本日志已公开，"
            "评审方可独立重跑抽取逻辑并与本文数字逐项比对；表 2 已收敛为纯日志派生，"
            "重跑结果不会因私有目录缺失而改变 |\n"
            "| 截图文件计数 | 原始 PNG 在私有 `_wbshots/`，**FACTS 不列该数字**；"
            "相关叙述见 N2 README §5 |\n"
            "| 表 3–9 输入 | 仍在**私有 Unity 仓库**与工程外暂存目录，"
            "公开仓库只有脚本与哈希，**不能独立重跑** |\n"
            "| 原始测量结果 | 未由外部独立复现；本节点只能核对公开材料内部的逻辑一致性 |\n"
            "| 图片 | 本节点零图片；表 4 / 表 8 的数字来自对 PNG 像素的脚本测量，"
            "不是对图片的主观描述 |\n")
    text = head + body + tail
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT, "lines", len(text.splitlines()))


if __name__ == "__main__":
    main()
