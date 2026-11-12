# FACTS — 机器产出，请勿手改

> 本文件由 `tools/make_facts.py` 生成。每个表都附生成命令；
> 数字与命令不一致时，以命令重跑结果为准，不要相信本文的文本。

| 项 | 值 |
|---|---|
| 生成时间 | 2026-11-12 06:40 UTC |
| Python | 3.13.14 |
| Pillow | 13.0.0 |
| 平台 | Windows-10-10.0.19045-SP0 |
| 测量器 | `tools/asset_lint.py`（确定性，无随机数） |

## 表 1 — 切面（spec=cutface，阈值见 SPEC §A）

```bash
python tools/asset_lint.py --spec cutface <A.png> <B.png>
```

| file | canvas | bbox | opaque | waist | waistPos | endTaper | solidity | compact | straight | edgeLum | colors | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| potato_cutface.png | 1024x1024 | 464,46,96,819 | 0.986 | 0.99 | 0.30 | 0.94 | 1.00 | 0.28 | 0.97 | 33 | #F0F0D0 #301000 #606050 | FAIL:straight,blunt_ends,dark_outline |
| _a2_committed.png | 1328x2112 | 0,0,1328,2112 | 0.856 | 0.94 | 0.45 | 0.41 | 0.99 | 0.20 | 0.29 | 23 | #F0F0C0 #F0F0B0 #F0F0D0 | FAIL:canvas,bbox,dark_outline |


第 2 行为**上一轮被否决的 A-2**（1328×2112，内容铺满全画布）。
原图体积 2.4MB，不放入本仓库；来源与校验：

| 项 | 值 |
|---|---|
| 来源 | 私有仓库 `d2f0145:ArtReview_Staging/PotatoArt_v06/CutFace_A2/potato_cutface_A2.png` |
| SHA256 | `539f2f842bf9ad1a451daeb674f4506f08ef443aed5827d4d3a68dfa9e5a4b70` |

## 表 2 — 现有正式丝束 6 张（spec=strip）

```bash
python tools/asset_lint.py --spec strip potato_strip_0{1..6}.png
```

| file | canvas | bbox | opaque | waist | waistPos | endTaper | solidity | compact | straight | edgeLum | colors | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| potato_strip_01.png | 512x512 | 130,202,260,115 | 0.657 | 0.84 | 0.64 | 0.22 | 0.76 | 0.05 | 0.17 | 18 | #E0C060 #F0D060 #301000 | FAIL:no_waist,loose_silhouette,ragged_edge,dark_outline |
| potato_strip_02.png | 512x512 | 138,190,248,123 | 0.558 | 0.77 | 0.59 | 0.25 | 0.66 | 0.05 | 0.07 | 11 | #301000 #E0D060 #402000 | FAIL:no_waist,loose_silhouette,ragged_edge,dark_outline |
| potato_strip_03.png | 512x512 | 122,184,276,130 | 0.470 | 0.71 | 0.36 | 0.15 | 0.58 | 0.04 | 0.02 | 10 | #301000 #E0D060 #402000 | FAIL:no_waist,loose_silhouette,ragged_edge,dark_outline |
| potato_strip_04.png | 512x512 | 123,203,258,113 | 0.600 | 0.83 | 0.69 | 0.26 | 0.70 | 0.05 | 0.16 | 12 | #E0C060 #F0D060 #301000 | FAIL:no_waist,loose_silhouette,ragged_edge,dark_outline |
| potato_strip_05.png | 512x512 | 99,201,276,114 | 0.581 | 0.83 | 0.30 | 0.12 | 0.71 | 0.05 | 0.03 | 17 | #E0C060 #F0D060 #402000 | FAIL:no_waist,loose_silhouette,ragged_edge,dark_outline |
| potato_strip_06.png | 512x512 | 118,201,284,137 | 0.462 | 0.73 | 0.45 | 0.17 | 0.55 | 0.04 | 0.08 | 12 | #E0C060 #F0D060 #402000 | FAIL:no_waist,loose_silhouette,ragged_edge,dark_outline |


## 表 3 — 参照图（证明阈值可达成，美术不可用）

```bash
python tools/asset_lint.py --spec cutface tools/ref_cutface_ellipse.png
python tools/asset_lint.py --spec strip tools/ref_bundle_topology.png
```

| file | canvas | bbox | opaque | waist | waistPos | endTaper | solidity | compact | straight | edgeLum | colors | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ref_cutface_ellipse.png | 1024x1024 | 464,46,96,819 | 0.787 | 0.92 | 0.30 | 0.27 | 1.01 | 0.23 | 0.32 | 217 | #F0E0B0 | PASS |


| file | canvas | bbox | opaque | waist | waistPos | endTaper | solidity | compact | straight | edgeLum | colors | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ref_bundle_topology.png | 512x512 | 126,203,261,106 | 0.772 | 0.66 | 0.48 | 0.25 | 0.94 | 0.41 | 0.13 | 203 | #F0D090 | PASS |


参照图是纯色实心 + 程序化轮廓，只用于证明「SPEC 的阈值集合存在可行解」。

## 表 4 — 文件清单与 SHA256

```bash
sha256sum tools/*.py tools/*.png N1_spec_freeze/*.md
```

| 文件 | 字节 | SHA256 |
|---|---|---|
| `asset_lint.py` | 7854 | `cdee417e5239cfe98827ab16a1f80985fe5f717fe5fe28ce4f6389fce045991b` |
| `make_facts.py` | 4576 | `0565f373b4441ddaf0f3e9da725129f50d5d8faaa283a2cb5c91c4c3b0be0f23` |
| `ref_bundle_topology.png` | 6774 | `e5745c1ad4c0a7c008980b48be228133bd911b84ef1e1ab0be61604a8875fddd` |
| `ref_cutface_ellipse.png` | 7106 | `1ab6d8109ce367abcf3cf641b564a440326a4fc948d067ac3e46e21f09451c30` |

## 复现步骤

1. 取 `Assets/Resources/Art/Unified_v2/food/stages/` 下 7 个文件（1 张 cutface + 6 张 strip）；
2. 跑上表命令，逐字比对输出；
3. 若数字与本文不一致，说明素材被改过 —— 执行方需说明改动来源。

