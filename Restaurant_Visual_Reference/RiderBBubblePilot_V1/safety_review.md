# RiderB Pilot — 工程安全复核

## 基线（本轮开始实测，未依赖历史）
- 主仓库：`E:/un/u/My project (1)`，分支 `refactor/data-driven-food`，HEAD `d2f014507388893dbcb053ae4929d81734efb8e6`。
- `git status --porcelain`（默认，未跟踪目录折叠为一项）：**212 项未提交**，与历史记录一致。
- 三张既有 clean 素材 MD5（开始 = 结束）：
  - Boy V3 `197305afc71dad9f3ffb795942171024`
  - Girl V2 `09eac2128e06c41c3152d8552a28bb52`
  - Uncle V1 `d95f53ae6bcc3641e81caa8547b0464d`
- 审阅仓：`cooking-review-publish`，开始 HEAD `f174a29a05adb465c80feb84514d99590b46b2c7`，工作区干净。
- Unity Editor：开始时未处于 Play（playing=False, screen 1920×1080）。

## 结束复核（本轮完成后）
- 主仓库分支、HEAD 未变；三张既有素材 MD5 未变；Play Mode 已退出（playing=False）。
- 审阅仓在提交本目录前 HEAD 仍为 `f174a29`，工作区干净。
- 未执行 `reset` / `clean` / `stash` / `rebase`；未提交或推送游戏主仓库。

## 关于“212 项未提交”计数守恒的说明
- 默认 `git status --porcelain` 会把整个未跟踪目录折叠为一项。`Assets/Resources/Art/Restaurant/` 本就是未跟踪目录（含 Boy/Girl/Uncle 等既有 untracked 素材），新增 `bubble_riderB_clean.png`(+.meta) 落在该目录内，不增加折叠后的项目数，故仍为 212。
- 用 `--untracked-files=all` 展开后为 2533 个文件；RiderB 新增项确认为：
  - `?? Assets/Resources/Art/Restaurant/bubble_riderB_clean.png`
  - `?? Assets/Resources/Art/Restaurant/bubble_riderB_clean.png.meta`
  - 修改：`M Assets/Scripts/CookingDemo/UIBuilder.cs`、`M Assets/Scripts/CookingDemo/DiningTable.cs`
  - 均为 RiderB 接入的预期改动；既有 212 项内容未被动过。

## 未改项确认
- Boy(index0)、Uncle(index1)、RiderY(index2)、Girl(index4) 的气泡素材与布局参数：未改（index2 仍 null）。
- CanvasScaler / 参考分辨率 / match：未改。
- 5:4 / 16:10 适配：未处理。
- RiderB / RiderY 的 GuestPos / BarPos / 耐心条参数：未改。
- 图标系统公共结构、`ServeOne`/`ManualTick` 等业务逻辑：未改。
- 虚拟鼠标测试未触碰实体鼠标；测试结束已移除虚拟设备、退出 Play。

## Git 操作
- 主仓库：仅读取状态/diff，无写操作、无提交、无推送。
- 审阅仓：仅向 `Restaurant_Visual_Reference/RiderBBubblePilot_V1/` 新增证据并提交推送。

## 结论
工程安全规则全部满足；未发现基线异常，无需恢复任何状态。
