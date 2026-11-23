# RiderY(index2) 工程安全复核

## 主仓库
- 路径：`E:/un/u/My project (1)`，分支 `refactor/data-driven-food`，HEAD `d2f014507388893dbcb053ae4929d81734efb8e6`
- 未提交数：normal `status --porcelain` = **212**（与本轮开始前基线一致）；
  展开未跟踪 `--untracked-files=all` = 2533 → 2535（+2：新增 `bubble_riderY_clean.png` 及其 Unity 生成 .meta，属预期接入改动）
- 未执行 reset / clean / stash / rebase；未提交、未推送主仓库；未覆盖或整理现有未提交改动。

## 四张既有素材 MD5（前后一致，未改动）
| 素材 | MD5 |
|---|---|
| bubble_boy_clean.png | 197305afc71dad9f3ffb795942171024 |
| bubble_girl_clean.png | 09eac2128e06c41c3152d8552a28bb52 |
| bubble_uncle_clean.png | d95f53ae6bcc3641e81caa8547b0464d |
| bubble_riderB_clean.png | 9571a3659d797006220dfd99c0707df1 |

## 新素材
- `bubble_riderY_clean.png`，MD5 `7aa672cf51db056f664cc26790db0a7e`（独立裁片清理，非复制 RiderB）

## 其他桌位
- 未修改 Boy/Girl/Uncle/RiderB 的素材与布局参数；`s_boyBubbleLayout` / `s_girlBubbleLayout` /
  `s_uncleBubbleLayout` / `s_riderBBubbleLayout` 源码保持不变；气泡数组中其余四项数值保持不变。
- 未处理 5:4 / 16:10 画幅、未改 CanvasScaler、未重构图标系统、未改 RiderY 之外桌位。

## 审阅仓库
- `cooking-review-publish`，本轮提交前 HEAD `b7e0713b496b700baced357f124bf8c6fc0eb5cb`、工作区干净
- 仅提交 `Restaurant_Visual_Reference/RiderYBubblePilot_V1/` 独立目录

## Play Mode
- 所有验证在 1920×1080 Play Mode 完成；结束后已退出 Play（playing=False）。

## 结论
工程安全约束全部满足；主仓库HEAD与未提交数守恒，既有素材零改动，无危险 Git 操作。
