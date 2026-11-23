# RiderB(index3) 动态气泡 Pilot V1 — 报告

> 本轮为餐厅右侧蓝骑手 RiderB（index3）接入独立动态订单气泡：独立诊断、独立 clean 素材、独立布局参数、Play Mode 显示/几何/交互/并行营业验证。
> **这是独立 Pilot，不代表批准扩展 RiderY 或其他桌位。**
> 主仓库 `E:/un/u/My project (1)`：分支 `refactor/data-driven-food`、HEAD `d2f0145`、212 项未提交；开始/结束 HEAD 与未提交数一致，三张既有 clean 素材 MD5 未变。未执行 reset/clean/stash/rebase，未提交或推送主仓库。详见 `safety_review.md`。

## 一、开始前基线复查（未依赖历史）
- 重读代码：`BuildTable` 中 index3 `bubbleRes=null`、无图标槽；`DiningTable.BindBubbleIcons()` 当时只有 girl/uncle/boy 三选一，index3 走 boy 默认但无槽位。
- 确认骑手规则：`SpawnNextGuest` 中 index 2/3 固定 `GuestKind.Takeout`；`MakeOrder(takeout=true)` 固定**单菜**；送达需外卖盒、半价入账、拿了就走。
- 底图定位：历史 4x 裁片经 FFT 匹配回 `restaurant_full.jpg`，MAE=0.92，最终裁片 bg (1038,340) 240×155。

## 二、阶段一：原始气泡诊断（只读）
- 椭圆主体 bg x[1051,1261] y[352,474]，中心≈(1156,413)，半轴 a≈105 b≈61；尾巴折线朝下偏左、尖端≈(1098,487)。
- 盘缘到描边 y=410 行左右间距 40/43px，清理空间充足。
- **关键风险**：顶部描边在 x≈1109–1183 与玻璃门竖条连通；右下描边在 x≈1252+ 被绿植遮挡；尾巴尖与骑手头盔上缘 y≈490 近接。故**不能用连通域取描边**，采用椭圆几何环 + 尾巴多边形保护。
- 证据：`analysis/geometry_grid_bgcoords.png`、`bubble_outline_vs_plant_8x.png`、`tail_vs_helmet_8x.png`、`plate_vs_outline_8x.png`、`top_outline_vs_doorframe_8x.png`、`original_bubble_4x.png`。

## 三、阶段二：独立 clean 素材
- `bubble_riderB_clean_candidate.png`，240×155，RGB 无 alpha，MD5 `9571a3659d797006220dfd99c0707df1`；非任何既有素材复用。
- 算法：几何描边/尾巴保护 → 盘子+盘缘+阴影清理核（半轴 90×54）→ 暖白带逐行插值渐变（顶部 RGB≈(252,245,237)）→ 8px 羽化合成。
- 自检：改动 37.13% 全在气泡内部；四边像素 max diff = 0（贴回无缝）；保护 12445px、尾巴 872px 完整。
- 视觉：盘菜清除干净、暖白渐变自然、描边/尾巴/绿植/门框完整，无黑边/锯齿/V 形/光晕。
- 对比与遮罩证据：`original_vs_candidate_4x.png`、`analysis/`。

## 四、阶段三：Unity 独立接入
- `UIBuilder.cs`：index3 气泡数组填 `bubble_riderB_clean`、坐标 (1038,585) 尺寸 240×155；其余桌原值不动。
- `DiningTable.cs`：新增 `s_riderBBubbleLayout`（bubbleW=240, iconCy=80, visible1=96 …），绑定加 index3 分支。
- 新增运行素材 1 张；未改公共系统、未改 CanvasScaler、未处理画幅适配、未推广 RiderY。
- 详见 `integration_notes.md`。

## 五、阶段四：运行时验证（1920×1080 Play Mode）

### A. 气泡显示 — 已通过
- RiderB 到店显示 clean 气泡（sprite=`bubble_riderB_clean`），底部原静态番茄炒蛋不再残留；单菜图标 `food_dish_tomato_egg` 清楚显示。
- Boy/Uncle/Girl 三桌气泡与图标同时正常显示，互不影响（截图 `play_screenshots/riderb_v1_all_four_with_icon_1920x1080.png`）。

### B. 图标几何 — 已通过（实际渲染像素差分）
- 可见像素 bbox `x1110..1205 y379..451`（96×73），4511 像素；仅在 RiderB 区域变化（boy/uncle/girl 差分 n=0）。
- 暖白安全区同宽度 y[366,464] 净高 98px；图标上下各留 **13px** 余量，完整落在暖白内。
- 距描边内缘约 13px、距绿植约 39px、距尾巴尖 30+px；不遮挡耐心条。
- 数据：`icon_visible_bounds.txt`；截图 `riderb_v1_bubble_zoom_4x.png`、`riderb_v1_icon_diff_overlay.png`。

### C. 交互与状态 — 已通过（独立虚拟鼠标，真实指针链）
- 虚拟 Mouse `RiderBDragVirtualMouse`（非 RawInput，device id 25），QueueStateEvent 注入按下/移动/松开；经 `PointerSystem.Update → HandleFrame → PickDraggable/BeginDrag → TryDrop → DropZone.OnDrop → TryServeBowlDish → ServeOne → TakeoutServed`；**未**调用 `ServeOne()`/`ManualTick()`。
- 结果：T3 `Waiting→Leaving`、`served=1`、图标灰化 `RGBA(0.50,0.50,0.50,1)`、气泡隐藏、`income=9`（外卖半价）、`readyCount=0`。
- 隔离：T0/T1/T4 状态、served、图标颜色、气泡显隐投喂前后完全一致。
- 灰化视觉截图：`riderb_v1_gray_icon_evidence.png`、`riderb_v1_gray_zoom_4x.png`（取证方式见 `virtual_input_verification.txt`）；骑手离场截图 `riderb_v1_after_virtual_feed_rider_left.png`。
- Console error = 0；虚拟设备结束时已移除。

### D. 并行营业 — 已通过
- Boy(双菜)/Uncle(单菜)/RiderB(单菜外卖)/Girl(三菜) 同时 Waiting，四套气泡与图标各自独立；RiderB 投喂送达只影响自身。
- Console error = 0。

## 六、结论分层

**已通过**
- 原始气泡诊断与几何实测；独立 clean 素材制作与四边无缝自检；Unity index3 独立接入；
- 1920×1080 单菜显示、图标实际像素边界、与描边/尾巴/绿植/耐心条的间距；
- 独立虚拟鼠标经真实指针链投喂、灰化、完成隐藏、状态隔离；四桌并行营业互不干扰；Console 0 错误。

**未通过**
- 无。（本轮没有验收失败项。）

**未验证**
- 实体鼠标真实拖拽体验（按任务要求不要求用户配合，不占用实体设备）。
- 骑手耐心耗尽（生气离场）路径的气泡隐藏。
- 骑手两菜/三菜（游戏逻辑固定单菜，visible2/3 未实测）。
- 灰化截图中气泡为取证重新显示（原流程送达即隐藏），已在 `virtual_input_verification.txt` 明确标注。

**已知瑕疵**
- 气泡底部内侧一条极淡暖灰弧线残留（`analysis/clean_bottom_residual_8x.png`），亮度接近天然内阴影，8x 下可见；与 Uncle V1 同类，是否 V2 清除交审阅判定。

**尚未处理的风险 / 推断**
- 本轮布局参数按 1920×1080 标定；5:4 / 16:10 表现未按任务范围处理。
- 虚拟鼠标 press/release 需跨真实帧边沿才稳定触发（首次自然满足，复跑曾边沿丢失，稳健跨帧后稳定）；属自动化输入时序要求，已在 `virtual_input_verification.txt` 记录，不影响实体游玩。
- 裁片贴回依赖既有 `Cover_3` 遮罩与气泡覆盖片同生命周期；本轮沿用既有框架，未改生命周期代码。

## 七、停止
本轮完成诊断 → 素材 → 接入 → Play 验证全链路；**未推广 RiderY、未扩展其他桌位、未改主仓库提交状态**。仅向审阅仓 `RiderBBubblePilot_V1/` 提交证据。停止，等待 ChatGPT 独立审阅。
