# Uncle 桌动态订单气泡 Pilot — 第一阶段报告

> 本轮把动态订单气泡扩展到 Uncle 桌（index1），独立制作单菜小气泡清理素材并接入现有动态绑定系统，验证单菜显示、灰化、隐藏与 Boy/Girl 独立性。
> **这是独立 Pilot，不代表批准扩展 RiderB / RiderY。**
> 游戏主仓库 `E:/un/u/My project (1)`：分支 `refactor/data-driven-food`、HEAD `d2f0145`、212 项未提交；开始前/结束后 status 逐行一致，HEAD 未变。Boy V3、Girl V2 素材 MD5 未变。未执行 reset/clean/stash/rebase，未提交或推送主仓库。详见 `workspace_check.md`。

## 一、开始前现状复查（未假设历史状态）
- 重新读取并确认当前实现：`UIBuilder.BuildTable` 中只有 index0/index4 有 clean 气泡覆盖片与动态图标槽；`DiningTable.BindBubbleIcons()` 用 `index==4 ? girl : boy` 二选一布局；Uncle(index1) 原本 `bubbleRes[1]=null`、无图标槽。
- 复查 Uncle 原始区域：从 1920×1080 底图裁切并用 FFT 模板匹配对回坐标 x[628,868) y[266,398)；实测气泡椭圆 x[637,855] y[273,375]、尾巴朝下偏左、尖端约 (705,392)，耐心条上缘 y≈390–391 与尾巴近接但不重叠；盘子与描边四边间距 13–24px。
- **重要纠正**：历史评估文档写 Uncle "尾朝下偏右"，实测为**朝下偏左**（见 `analysis/bubble_geometry_grid.png`、`analysis/tail_vs_patience_bar_8x.png`）。本轮以像素实测为准。
- 特殊风险：Uncle 气泡描边与背景玻璃门框在深色连通域上相连，不能像 Boy/Girl 那样直接用连通域取描边，改用椭圆几何环 + 暗像素核心 + 尾巴多边形保护。

## 二、素材（事实）
- 独立制作 `bubble_uncle_clean_candidate.png`（240×132，MD5 `d95f53ae6bcc3641e81caa8547b0464d`），非 Boy/Girl 素材复用。
- 算法：描边/尾巴几何保护 → 盘子核 + 8px 羽化 → 严格暖白像素高斯场重建 → 合成。技术细节见 `material_spec.md`。
- 结果：改动像素 30.01%，改动 bbox 完全在气泡内部（底图 [657,286]–[825,366]），四边首末像素 100% 保持原样，贴回无缝。
- 视觉自检：描边与尾巴完整连续，无清理破坏；盘子与盘缘清除干净；暖白渐变自然，无 Boy V2 那种黑锯齿环、无 Girl V1 那种 V 形/椭圆硬边。
- **已知轻微残留**：盘缘底部留一条极淡暖灰阴影（`analysis/residual_bottom_8x.png`），亮度接近气泡天然内阴影，4× 下极轻微。未擅自大范围修补，交审阅判定。左右描边近处无残留（`analysis/residual_left_8x.png`、`residual_right_8x.png`）。
- 对比图：`original_vs_candidate_4x.png`；几何/遮罩/重建证据在 `analysis/`。

## 三、集成（事实）
- 新增运行素材 1 个，修改 C# 2 个文件（仅必需行）：
  - `UIBuilder.cs`：气泡数组填 index1，位置 x=628 y=682 尺寸 240×132
  - `DiningTable.cs`：新增 `s_uncleBubbleLayout`（bubbleW=240、iconCy=80、visible1=112 …），绑定按 index1 选用
- 素材、坐标、图标布局参数全套独立，与 Boy/Girl 不共享具体数值；绑定/灰化/隐藏生命周期逻辑复用既有实现。
- 未改 CanvasScaler / 画幅，未处理 5:4、16:10，未动 Boy/Girl 参数与 RiderY/RiderB。见 `integration_notes.md`。

## 四、Play Mode 验证（事实，1920×1200 运行时）
- 单菜显示：Uncle 到店订单"青椒炒肉"，气泡 `bubble_uncle_clean` 显示，内部单个圆形菜品图标 `food_dish_pepper_beef`，无静态盘子残留；图标在气泡内、未压尾巴（结构读数 + 截图双重确认）。
- 灰化：`ServeOne` 后 Uncle 图标变 RGBA(0.50,0.50,0.50,1)；Boy、Girl 图标保持 (1,1,1,1)，未受影响。
- 隐藏：上齐后 `StartEating`→`ManualTick` 推进，Uncle 进入 CoinAndTrash，气泡与图标一起隐藏；Boy/Girl 仍 Waiting、气泡仍显示。
- 同时营业：五桌全部到店，Boy(双菜)/Girl(三菜)/Uncle(单菜) 三套气泡与图标各自独立，无串扰。
- Console error = 0。
- 截图 3 张见 `play_screenshots/`，原始读数见 `runtime_log.txt`。

## 五、推断 / 未验证
- **推断**：Uncle 的独立布局参数（iconCy=80、visible1=112）基于 1920×1080 参考系标定；在 5:4、16:10 画幅下的表现本轮未测（按任务范围不处理适配）。
- **未验证**：真实 OS 鼠标拖拽投喂（本轮用源码同一入口 `ServeOne` 验证灰化，未做 OS 级拖拽；Boy/Girl 既有 Pilot 已完成真实拖拽验证，本轮未重复）。
- **未验证**：Uncle 生气离场（耐心耗尽）路径下的气泡隐藏；本轮走的是正常上齐→用餐→离场路径。
- **未验证**：Uncle 两菜/三菜订单（本桌定位为单菜桌，本轮只注入单菜）；`s_uncleBubbleLayout` 已给 visible2/visible3 参数但未实测。
- 审阅判定项：底部极淡盘缘阴影是否需要在 V2 进一步清除。

## 六、状态声明
- 本轮完成素材制作 + Unity 接入 + Play 验证，未推广 RiderB/RiderY。
- 主仓库未提交/推送；证据与代码改动保留在工作区，供独立审阅。
- **停止，等待 ChatGPT 独立审阅；本轮不实施任何修复推广。**
