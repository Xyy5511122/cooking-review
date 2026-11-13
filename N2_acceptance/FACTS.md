# FACTS — 机器产出，请勿手改

> 本文件由 `tools/make_n2_facts.py` 生成；每个表附生成命令与输入 SHA256。
> 数字与命令重跑结果不一致时，以重跑结果为准，不要相信本文文本。

| 项 | 值 |
|---|---|
| 生成时间(UTC) | 2026-11-13 05:32:44 UTC |
| Python | 3.13.14 |
| 平台 | Windows-10-10.0.19045-SP0 |
| 生成脚本 SHA256 | `c41d505754838531b71cae8dcd65a83f400dce763b058bb9d04a96be1bccfc4f` |
| 节点 | N2 产出验收：青椒 S7–S12 / v08 |

## 表 1 — 编译 / 探针 / 自测（脚本读日志原文）

```bash
python tools/make_n2_facts.py verify
```

输入 SHA256（前 12 位）： `cooking/s12_verify.log`=034cd27742ad， `tools/make_n2_facts.py`=c41d50575483

| 项 | 实测 | SPEC 期望 |
|---|---|---|
| 控制台日志条数（逐次读取） | 0,0,0,0 | 全部为 0 |
| Unity 编辑态 | False / False | compiling=False playing=False |
| FULLRECT | 33/33 | 33/33 |
| missing | 0 | 0 |
| S11 CHANGED SPRITES 可加载 | 12/12 | 12/12 |
| DevSelfTest lines | 300 | 300 |
| DevSelfTest PASS | 300 | 300 |
| DevSelfTest FAIL | 0 | 0 |

## 表 2 — 干净 Play Mode 实机日志与截图计数

```bash
python tools/make_n2_facts.py live
```

输入 SHA256（前 12 位）： `cooking/s12_live.log`=1f0ac6648a77， `tools/make_n2_facts.py`=c41d50575483

| 项 | 实测 |
|---|---|
| 实机日志 cap_ 帧数 | 20 |
| whiteFlash=False 出现次数 | 20 |
| sheetMode=True 出现次数 | 11 |
| sheetNow 分段帧集合 | 1,2,3,4,5 |
| stripsOn=8 出现 | True |
| 末帧入备料位 | True |
| _wbshots/s12/*.png | 20 |
| _wbshots/s12_before/*.png | 20 |

## 表 3 — 素材字节一致性（逐张 SHA256）

```bash
python tools/make_n2_facts.py sprites
```

输入 SHA256（前 12 位）： `GreenPepper_v08/spec_v8.json`=b85d7b995f99， `GreenPepper_v08/green_pepper_prep_hand.png`=39da635218a8， `GreenPepper_v07/green_pepper_prep_hand.png`=98798218731e， `cooking/_s12_v7_baseline.json`=7839180977b9

| 项 | 实测 | SPEC 期望 |
|---|---|---|
| v08 PNG 数 | 33 | 33 |
| v07 PNG 数 | 33 | 33 |
| v08 vs v07 变化集合 | green_pepper_prep_hand.png | 仅 green_pepper_prep_hand.png |
| 正式 stages 青椒 PNG 数 | 32 | 32 |
| v08 vs 正式 stages SHA 不一致 | (空) | (空) |
| spec_v8.json 条目 | 33 | 33 |
| spec_v8.json SHA 不匹配 | (空) | (空) |
| v07 37 文件基线变化 | (空) | (空) |
| v08 33 张 SHA 串接摘要 | 89db2bfde79fff5b… | 可复算 |

## 表 4 — 手部几何（PIL + numpy 实测；alpha>20，肤色阈值见脚本）

```bash
python tools/make_n2_facts.py hand
```

输入 SHA256（前 12 位）： `GreenPepper_v07/green_pepper_prep_hand.png`=98798218731e， `GreenPepper_v08/green_pepper_prep_hand.png`=39da635218a8

| 项 | 实测 | 期望 |
|---|---|---|
| v07 肤色重心 (x,y) | [593, 511] | 593,511 |
| v08 肤色重心 (x,y) | [430, 511] | 430,511 |
| v07 alpha bbox min/max（含端点） | [70, 348, 837, 816] | — |
| v08 alpha bbox min/max（含端点） | [186, 348, 953, 816] | — |
| v07 alpha bbox 半开 [x0,y0,x1,y1) | [70, 348, 838, 817] | — |
| v08 alpha bbox 半开 [x0,y0,x1,y1) | [186, 348, 954, 817] | — |
| v08 == v07 水平镜像（逐像素） | True | True |
| 抓握 y 是否等于主体中点 | True | True |

> 口径：`S12_report.md` / `spec_v8.json.handFraming` 用**半开** bbox，上面前两行是含端点的 min/max，两者相差 1px，不是矛盾。`spec_v8.json.files[].bbox` 则是第三种口径 `[x,y,宽,高]`（alpha>8），不可混用。

## 表 5 — 工程保护状态（直接跑 git / stat）

```bash
python tools/make_n2_facts.py git
```

输入 SHA256（前 12 位）： `tools/make_n2_facts.py`=c41d50575483

| 项 | 实测 | 期望 |
|---|---|---|
| HEAD | d2f0145 art(potato): add CutFace A2 candidate (vertical oval cross-section) | 以 d2f0145 开头 |
| branch | refactor/data-driven-food | refactor/data-driven-food |
| git status --short 行数 | 93 | >0（未提交） |
| 已暂存文件数 | 0 | 0 |
| potato_base_1024.png mtime | 2026-11-01 16:53 | 2026-11-01 16:53 |
| food_raw_beef.png mtime | 2026-11-01 16:53 | 2026-11-01 16:53 |

## 表 6 — 输入文件清单与 SHA256（复算入口）

```bash
python tools/make_n2_facts.py inputs
```

输入 SHA256（前 12 位）： `tools/make_n2_facts.py`=c41d50575483

| 文件 | 字节 | SHA256 |
|---|---|---|
| `tools/make_n2_facts.py` | 12273 | `c41d505754838531b71cae8dcd65a83f400dce763b058bb9d04a96be1bccfc4f` |
| `cooking/s12_verify.log` | 5486 | `034cd27742ad124960a9dadcf7e4704ed783e4b259b20d81d2677694508fab5c` |
| `cooking/s12_live.log` | 17155 | `1f0ac6648a77cfadc65253d08325c9d10852248b634dd08a58462c9c4a537465` |
| `GreenPepper_v08/spec_v8.json` | 18075 | `b85d7b995f9907e27af8a0177b2b1114680d6fa77878256efff590e6f2e8838c` |
| `GreenPepper_v08/green_pepper_prep_hand.png` | 238036 | `39da635218a84b532e069add1213d88b9429671865afc4c252fa35509f871123` |
| `GreenPepper_v07/green_pepper_prep_hand.png` | 240424 | `98798218731ed5c2c7c0f8c9801c28b02f4fe30c76f4dcc3e90094a8fbdec1d5` |
| `cooking/_s12_v7_baseline.json` | 3635 | `7839180977b9aa5091faa1968a65b64598c81438d0abd93dd39960c31de7cb31` |
| `cooking/S12_report.md` | 7197 | `ceada3a4bcc96a0bc1790d5ef4530859c0eadc415abd91f0d06a4f8b3b27d569` |
| `cooking/S12_spec.md` | 4599 | `7c2295c8d51d84459515595f93b20dc41ca4703e8f4ba8a0873c371d218e398b` |

## 复现步骤与边界

```bash
cd <public-review-repo>
python tools/make_n2_facts.py            # 重写 FACTS.md
python tools/make_n2_facts.py verify     # 只打印表 1
```

| 边界 | 说明 |
|---|---|
| 输入位置 | 表 1–5 的输入全部在**私有 Unity 仓库**与工程外暂存目录，公开仓库只有脚本与哈希 |
| 评审方可复现性 | **不能独立重跑**，只能核对命令、输入 SHA256 与逻辑自洽；见 N2 README 主张 C5 |
| 图片 | 本节点零图片；表 4 的数字来自对 PNG 像素的脚本测量，不是对图片的主观描述 |
