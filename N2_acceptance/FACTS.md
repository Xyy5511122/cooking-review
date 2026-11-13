# FACTS — 机器产出，请勿手改

> 本文件由 `tools/make_n2_facts.py` 生成；每个表附生成命令与输入 SHA256。
> 数字与命令重跑结果不一致时，以重跑结果为准，不要相信本文文本。

| 项 | 值 |
|---|---|
| 生成时间(UTC) | 2026-11-13 05:49:32 UTC |
| Python | 3.13.14 |
| 平台 | Windows-10-10.0.19045-SP0 |
| 生成脚本 SHA256 | `4b9f8d09006ade4c163ccc84d5dc5998ccf0b6718341991809ab167ca70d44e9` |
| 对应 SPEC 版本 | v2（CONDITIONAL 修订） |
| 节点 | N2 产出验收：青椒 S7–S12 / v08 |

## 表 1 — 编译 / 探针 / 自测（脚本读日志原文；日志已公开）

```bash
python tools/make_n2_facts.py verify
```

输入 SHA256（前 12 位）： `evidence/s12_verify.log`=034cd27742ad， `tools/make_n2_facts.py`=4b9f8d09006a

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

## 表 2 — 干净 Play Mode 实机日志（纯公开输入，可独立重跑）

```bash
python tools/make_n2_facts.py live
```

输入 SHA256（前 12 位）： `evidence/s12_live.log`=1f0ac6648a77， `tools/make_n2_facts.py`=4b9f8d09006a

| 项 | 实测 |
|---|---|
| 实机日志 cap_ 帧数 | 20 |
| whiteFlash=False 出现次数 | 20 |
| sheetMode=True 出现次数 | 11 |
| sheetNow 分段帧集合 | 1,2,3,4,5 |
| stripsOn=8 出现 | True |
| 末帧入备料位 | True |

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

输入 SHA256（前 12 位）： `tools/make_n2_facts.py`=4b9f8d09006a

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

输入 SHA256（前 12 位）： `tools/make_n2_facts.py`=4b9f8d09006a

| 文件 | 字节 | SHA256 |
|---|---|---|
| `tools/make_n2_facts.py` | 24776 | `4b9f8d09006ade4c163ccc84d5dc5998ccf0b6718341991809ab167ca70d44e9` |
| `evidence/s12_verify.log` | 5486 | `034cd27742ad124960a9dadcf7e4704ed783e4b259b20d81d2677694508fab5c` |
| `evidence/s12_live.log` | 17155 | `1f0ac6648a77cfadc65253d08325c9d10852248b634dd08a58462c9c4a537465` |
| `GreenPepper_v08/spec_v8.json` | 18075 | `b85d7b995f9907e27af8a0177b2b1114680d6fa77878256efff590e6f2e8838c` |
| `GreenPepper_v07/spec_v7.json` | 15071 | `102492e8fd959f3e3770d8ad8e84641172fcf965054896051cfd122ed77638ac` |
| `GreenPepper_v08/green_pepper_prep_hand.png` | 238036 | `39da635218a84b532e069add1213d88b9429671865afc4c252fa35509f871123` |
| `GreenPepper_v07/green_pepper_prep_hand.png` | 240424 | `98798218731ed5c2c7c0f8c9801c28b02f4fe30c76f4dcc3e90094a8fbdec1d5` |
| `GreenPepper_v08/green_pepper_prep_whole.png` | 623154 | `9d44d1ac868621e141ff51bd4b4087b88cec17d76ef1d086646d1fefb7d2a600` |
| `GreenPepper_v08/green_pepper_prep_headless.png` | 703658 | `eabb5c397d57b12acd46eec037416f75a0d3b35881e01007cb1aa8354380e012` |
| `GreenPepper_v08/green_pepper_prep_no_butt.png` | 803016 | `4a297786bc0a41cbb8fb25414c26b224e7ea1e169306d81a97cccbe812c9a4fc` |
| `GreenPepper_v08/green_pepper_prep_head_piece.png` | 110214 | `1ad16fbf8cce4fdb1965f9421b6af28094a6f7d3fa6e8cd024542eacac61edc2` |
| `GreenPepper_v08/green_pepper_prep_butt_piece.png` | 109770 | `a319bd43f85d6db6556a1e782681ae730e9ae49aba51a6fc19b9bb0f18aa5e9a` |
| `cooking/_s12_v7_baseline.json` | 3635 | `7839180977b9aa5091faa1968a65b64598c81438d0abd93dd39960c31de7cb31` |
| `_S12_backup/stages/green_pepper_prep_hand.png` | 240424 | `98798218731ed5c2c7c0f8c9801c28b02f4fe30c76f4dcc3e90094a8fbdec1d5` |
| `cooking/S12_report.md` | 7197 | `ceada3a4bcc96a0bc1790d5ef4530859c0eadc415abd91f0d06a4f8b3b27d569` |
| `cooking/S12_spec.md` | 4599 | `7c2295c8d51d84459515595f93b20dc41ca4703e8f4ba8a0873c371d218e398b` |

## 表 7 — S12 变更集合（起点快照 45 文件逐 SHA + 全 Assets mtime 扫描）

```bash
python tools/make_n2_facts.py changes
```

输入 SHA256（前 12 位）： `_S12_backup/stages/green_pepper_prep_hand.png`=98798218731e， `food/stages/green_pepper_prep_hand.png`=39da635218a8， `CookingDemo/PrepStepsController.cs`=42da39a87dbd， `PrepChoreography/green_pepper.asset`=9146708b046c

| 项 | 实测 | 说明（**非期望值，不产生判定**） |
|---|---|---|
| S12 起点快照文件数 | 45 | 快照规模 |
| 快照逐文件 SHA 变化集合 | stages/green_pepper_prep_hand.png | 回答评审 [2] |
| 快照中 C# 文件数 / 变化数 | 6 / 0 | 覆盖 6 个切配 C# |
| 快照中 .asset 文件数 / 变化数 | 2 / 0 | 覆盖 2 个青椒资产 |
| 快照中 PNG 文件数 / 变化数 | 33 / 1 | 33 张青椒 PNG |
| 快照中 v07 review 文本数 / 变化数 | 4 / 0 | 历史验收快照 |
| S12 起点时刻 | 2026-11-13 13:14:33 | mtime 扫描基线 |
| Assets/ 下 mtime 晚于起点的文件 | Resources/Art/Unified_v2/food/stages/green_pepper_prep_hand.png | 全目录扫描，含 .meta |
| 其中 .cs / .asset / .meta 数 | 0 | 回答评审 [2] |
| 相对 HEAD 的 git status 行数（历史遗留，口径不同） | 93 | 不用于 S12 判定 |
| 相对 HEAD 的 cs/asset/meta 计数（累计未提交） | 15/16/14 | 不用于 S12 判定 |

> 口径：`_S12_backup/` 是 S12 动手前的 45 文件快照；「变化」= 与该快照逐文件 SHA256 不一致。`git status` 是**相对 HEAD d2f0145 的累计未提交改动**（含 S7–S11 遗留），不能拿来证明或否定 S12 本轮改动。`.meta` 不在快照内，用 Assets/ 全量 mtime 扫描补足。**本表只补证据，N2-01..16 的期望值与判定方式不变。**

## 表 8 — 素材层可见性代理量（alpha>20；浅内壁阈值沿用 S11）

```bash
python tools/make_n2_facts.py visibility
```

输入 SHA256（前 12 位）： `GreenPepper_v07/spec_v7.json`=102492e8fd95， `GreenPepper_v08/green_pepper_prep_hand.png`=39da635218a8， `GreenPepper_v08/green_pepper_prep_whole.png`=9d44d1ac8686， `GreenPepper_v08/green_pepper_prep_headless.png`=eabb5c397d57， `GreenPepper_v08/green_pepper_prep_no_butt.png`=4a297786bc0a， `GreenPepper_v08/green_pepper_prep_head_piece.png`=1ad16fbf8cce， `GreenPepper_v08/green_pepper_prep_butt_piece.png`=a319bd43f85d

| 项 | 实测（总像素 / 未被手层遮挡） | 说明（**非期望值，不产生判定**） |
|---|---|---|
| 手层 alpha>20 覆盖像素数 | 151580 | 遮挡基准 |
| 整椒顶部 y<308（果梗/头顶）alpha / 未被手遮挡 | 50398 / 50398 | 回答评审 [3] |
| 整椒底部 y>714（圆底）alpha / 未被手遮挡 | 75026 / 65358 | 回答评审 [3] |
| 上切口带 y=300..368 的浅内壁像素 / 未被遮挡（headless） | 7383 / 6885 | 回答评审 [3] |
| 上切口带 y=300..368 的浅内壁像素 / 未被遮挡（no_butt） | 7383 / 6885 | 回答评审 [3] |
| 下切口带 y=664..724 的浅内壁像素 / 未被遮挡（no_butt） | 6645 / 5375 | 回答评审 [3] |
| 同窗口对照（headless，尚未切尾） | 85 / 81 | 状态差异对照 |
| 椒头落料 alpha / 未被手遮挡 | 39753 / 39753 | 回答评审 [3] |
| 底片环落料 alpha / 未被手遮挡 | 43244 / 40140 | 回答评审 [3] |

> 口径：切口窗口由 `spec_v7.json.cutY`（head=308 / butt=714）派生；浅内壁阈值是 S11 报告的复算参数，**不是验收阈值**。这些数字只证明素材层存在未被手图层遮挡的像素，**不证明 UGUI 实际渲染可见、不证明用户视觉上可见**；实机呈现由用户目视验收。**本表只补证据，不新增判定条款。**

## 表 9 — 两次签核字段实际值与 spec 输入哈希

```bash
python tools/make_n2_facts.py signoff
```

输入 SHA256（前 12 位）： `GreenPepper_v07/spec_v7.json`=102492e8fd95， `GreenPepper_v08/spec_v8.json`=b85d7b995f99

| 项 | 实测 | 说明（**非期望值，不产生判定**） |
|---|---|---|
| spec_v7.json SHA256（完整） | 102492e8fd959f3e3770d8ad8e84641172fcf965054896051cfd122ed77638ac | 评审 [4] 要求的输入哈希 |
| spec_v8.json SHA256（完整） | b85d7b995f9907e27af8a0177b2b1114680d6fa77878256efff590e6f2e8838c | 输入哈希 |
| spec_v7.json.acceptance.signedOffBy | user | 字段原值 |
| spec_v7.json.acceptance.signedOffAt | 2026-11-13T13:07:00+08:00 | 第一次签核 |
| spec_v7.json.acceptance.closedRequirements | REQ-S11-01,REQ-S11-02,REQ-S11-03,REQ-S11-04 | 第一次关闭的需求 |
| spec_v8.json.acceptance.signedOffAt（v07 历史副本） | 2026-11-13T13:07:00+08:00 | 与 v07 相同，非第三次签核 |
| spec_v8.json.s12Acceptance.signedOffBy | user | 字段原值 |
| spec_v8.json.s12Acceptance.signedOffAt | 2026-11-13T13:22:47+08:00 | 第二次签核 |
| spec_v8.json.s12Acceptance.closedRequirements | REQ-S12-01 | 第二次关闭的需求 |
| v08.acceptance == v07.acceptance（说明是副本，非第三次签核） | True | 字段等值比较 |
| 两次签核时间不同 | True | 独立登记核对 |
| 两次关闭需求集合不相交 | True | 独立登记核对 |
| v07 status 字段前缀 | ACCEPTED / frozen | ACCEPTED / frozen |
| v08 status 字段前缀 | ACCEPTED / frozen | ACCEPTED / frozen |

> 口径：`spec_v8.json` 内同时含 `acceptance`（v07 签核副本）与 `s12Acceptance`（第二次签核）；两者时间不同、关闭需求不相交。**本表只补证据，不新增判定条款。**

## 复现步骤与边界

```bash
cd <public-review-repo>
python tools/make_n2_facts.py verify   # 表 1：公开日志，可独立重跑
python tools/make_n2_facts.py live     # 表 2：公开日志，可独立重跑
python tools/make_n2_facts.py changes  # 表 7：需要私有工程，公开环境会拒绝
N2_PUBLIC_ONLY=1 python tools/make_n2_facts.py changes  # 演示拒绝边界
python tools/make_n2_facts.py          # 全表重写（仅执行方）
```

| 边界 | 说明 |
|---|---|
| 表 1 / 表 2 输入 | `N2_acceptance/evidence/` 两份纯文本日志已公开，评审方可独立重跑抽取逻辑并与本文数字逐项比对；表 2 已收敛为纯日志派生，重跑结果不会因私有目录缺失而改变 |
| 截图文件计数 | 原始 PNG 在私有 `_wbshots/`，**FACTS 不列该数字**；相关叙述见 N2 README §5 |
| 表 3–9 输入 | 仍在**私有 Unity 仓库**与工程外暂存目录，公开仓库只有脚本与哈希，**不能独立重跑** |
| 原始测量结果 | 未由外部独立复现；本节点只能核对公开材料内部的逻辑一致性 |
| 图片 | 本节点零图片；表 4 / 表 8 的数字来自对 PNG 像素的脚本测量，不是对图片的主观描述 |
