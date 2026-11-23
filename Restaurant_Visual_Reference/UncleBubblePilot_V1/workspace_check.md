# 工程前后安全复核 — Uncle 气泡 V1 Pilot

## 主仓库状态（开始 / 结束一致）
- 仓库：`E:/un/u/My project (1)`
- 分支：开始 `refactor/data-driven-food` → 结束 `refactor/data-driven-food`
- HEAD：开始 `d2f014507388893dbcb053ae4929d81734efb8e6` → 结束 `d2f014507388893dbcb053ae4929d81734efb8e6`
- 未提交改动数：开始 212 → 结束 212（`git status --porcelain` 行数）
- 完整 status 快照：`status_before.txt` / `status_after.txt`（工作区本地），两者 `diff` 为空，逐行一致

## 基线素材 MD5（未改动）
- Boy V3 `bubble_boy_clean.png`：`197305afc71dad9f3ffb795942171024`（开始=结束）
- Girl V2 `bubble_girl_clean.png`：`09eac2128e06c41c3152d8552a28bb52`（开始=结束）

## 本轮新增 / 修改文件（全部在主仓库工作区，未提交）
新增：
- `Assets/Resources/Art/Restaurant/bubble_uncle_clean.png`（运行素材，MD5 `d95f53ae6bcc3641e81caa8547b0464d`）
- `Assets/Resources/Art/Restaurant/bubble_uncle_original.png`（原始裁片对照，非运行必需）

修改（仅 2 个 C#，改动行见 integration_notes.md）：
- `Assets/Scripts/CookingDemo/UIBuilder.cs`
- `Assets/Scripts/CookingDemo/DiningTable.cs`

按文件修改时间核对，本轮 23:30 之后工程内仅上述 4 个文件发生变化（其余文件时间均早于本轮）。

## 禁止项核对
- 未执行 `reset` / `clean` / `stash` / `rebase`：是
- 未覆盖或清理既有未提交工作：是（212 项完整保留，status 逐行一致）
- 未提交或推送主仓库：是（HEAD 未变）
- 未创建 Recovery：是（`Assets/_Recovery` 创建于 2026-10-10、最后修改 16:02，本轮开始前已存在于 status 快照中）
- 未改 CanvasScaler / 画幅策略：是
- 未处理 5:4 / 16:10：是
- 未改 Boy / Girl 参数，未推广 RiderY / RiderB：是

## 审阅仓库
- 交付目录：`Restaurant_Visual_Reference/UncleBubblePilot_V1/`（独立新建）
- 提交/推送：本目录证据提交到 `cooking-review-publish` 仓库 `main`，不触碰游戏主仓库
