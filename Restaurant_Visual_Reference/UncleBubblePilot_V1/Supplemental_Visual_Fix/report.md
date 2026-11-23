# Uncle 气泡 V1：单菜图标越界修正报告

> 本轮只修正 Uncle(index1) 的独立图标布局参数；未改气泡清理素材、未改气泡坐标、未改 CanvasScaler、未改 Boy/Girl 共享参数或公共默认值、未重构图标系统、未处理 5:4 / 16:10、未改 RiderB/RiderY。
> 交付后已退出 Play Mode；游戏主仓库未提交、未推送。

## 一、结论速览

| 项 | 结果 |
|---|---|
| 单菜可见像素 | 修正前 `x 692..803, y 262..345`（112×84）；修正后 `x 712..783, y 280..345`（72×66） |
| 是否仍在暖白内部 | 修正后是。该 x 范围内暖白内缘 `y 278..345`；顶部余量 2px，底边落在最后一个暖白行，未越出 |
| 是否压住描边 | 修正后否。到暖白/描边内缘最小距离约 1px；修正前图标顶部压入暖白内缘 20px |
| 是否接触尾巴 | 否。到尾部暗色像素最小距离约 25px（修正前后均为 25px） |
| 视觉居中 | 修正后中心 `(747.5, 312.5)`，暖白安全区中心 `y 311.5`，偏差约 1px |
| Boy/Girl 并存 | 不受影响；三桌同时营业，状态与图标颜色前后一致 |
| Console error | 0（全流程） |
| 虚拟鼠标拖拽 | 已通过；Uncle 灰化，Boy/Girl 不受影响 |

## 二、工程基线（前 / 后一致）

- 主仓库：`E:/un/u/My project (1)`
- 分支：`refactor/data-driven-food`
- HEAD：`d2f014507388893dbcb053ae4929d81734efb8e6`
- 未提交项：212（结束复核仍为 212）
- 三张清理素材 MD5（结束复核未变）：
  - Boy V3 `bubble_boy_clean.png`：`197305afc71dad9f3ffb795942171024`
  - Girl V2 `bubble_girl_clean.png`：`09eac2128e06c41c3152d8552a28bb52`
  - Uncle V1 `bubble_uncle_clean.png`：`d95f53ae6bcc3641e81caa8547b0464d`
- 审阅仓起始 HEAD：`235023f49f002331546e8cf1ad00732d94393969`，工作区干净
- 未执行 reset / clean / stash / rebase；未提交或推送游戏主仓库

## 三、改动范围

仅改 `Assets/Scripts/CookingDemo/DiningTable.cs` 中 `s_uncleBubbleLayout` 的两个值：

| 参数 | 修改前 | 修改后 |
|---|---:|---:|
| `bubbleW` | 240f | 240f（未改） |
| `iconCy` | 80f | **82f** |
| `visible1` | 112f | **72f** |
| `visible2` | 90f | 90f（未改） |
| `visible3` | 68f | 68f（未改） |
| `gap2` | 12f | 12f（未改） |
| `gap3` | 5f | 5f（未改） |

未改 `s_boyBubbleLayout`、`s_girlBubbleLayout`、`s_bubbleIconFits`、`ApplyBubbleIconFit()`、`UIBuilder.cs` 中气泡数组/坐标/尺寸、`GameBootstrap.cs` 的 CanvasScaler、任何 PNG 素材或 RiderB/RiderY。

## 四、为什么不是只调 `iconCy`

`ApplyBubbleIconFit()` 用 `visibleW` 决定外层 RectTransform 的尺寸，再按 sprite alpha 中心补偿位置。`iconCy` 只平移中心，不会缩小非透明像素；当前实际可见高度为 84px，而 Uncle 气泡该宽度下的暖白净高只有约 67px，单靠移动无法同时满足上下边界。因此本轮同时缩小 `visible1` 并重定 `iconCy`。

## 五、可见边界测量方法

为避免透明边/纹理推算误差，本轮采用**实际渲染像素差分**：

1. 1920×1080 Play Mode，`Canvas.scaleFactor=1.000000`；三桌同时到店（Boy 双菜、Uncle 单菜、Girl 三菜）。
2. 冻结时间轴，分别在 Uncle 单菜单个 `dishIconRoots[0]` 显示 / 隐藏状态截取全屏图。
3. 对两张截图逐像素取 `max(|ΔR|,|ΔG|,|ΔB|)>12` 的包围盒，即为图标真实可见像素范围。
4. 用隐藏图标的截图在气泡区域内做暖白像素分类，得到暖白内缘；用暗色像素分类得到描边/尾巴距离。

> 说明：补充验证 `235023f` 用 `Sprite.textureRect` + alpha 包围盒推算得到“越出 Rect 约 14px”。本轮用实际渲染差分得到“越出 Rect 顶 4px、压入暖白内缘 20px”。两者口径不同，但都指向同一事实：修正前圆盘真实像素覆盖/越出描边，因此按实际渲染像素修正。

### 运行时几何（实测）

- bubble Rect：`x 628..868`，bottom-origin `y 682..814`，屏幕 `y 266..398`
- 修正前 icon Rect：`x 681.936..814.065`，bottom-origin `y 695.936..828.065`，`sizeDelta=132.129×132.129`
- 修正后 icon Rect：`x 705.530..790.470`，bottom-origin `y 721.530..806.470`，`sizeDelta=84.940×84.940`，`anchoredPosition=(120,82)`

### 边界数据

| 指标 | 修正前 | 修正后 |
|---|---:|---:|
| 可见像素 bbox（屏幕 x） | 692..803 | 712..783 |
| 可见像素 bbox（屏幕 y） | 262..345 | 280..345 |
| 可见尺寸 | 112×84 | 72×66 |
| 相对 bubble Rect 顶部 | 越出 4px | 内缩 14px |
| 暖白内缘（同 x 范围） | y 282..345 | y 278..345 |
| 顶部余量 | -20px（压描边） | +2px |
| 底部余量 | 0px | 0px（止于最后暖白行，未越出） |
| 到暖白/描边内缘最小距离 | 0.00px | 1.00px |
| 到尾巴暗像素最小距离 | 25.00px | 25.00px |
| 可见中心 | (747.5, 303.5) | (747.5, 312.5) |

## 六、视觉验证（1920×1080 Play Mode）

- `before_single_dish_1920x1080.png`、`after_single_dish_1920x1080.png`：修正前后全屏
- `before_after_full.png`：左右并列全屏对比
- `before_after_zoom.png`：气泡局部 3× 并列对比（左修正前、右修正后）
- `after_zoom_annotated.png`：修正后局部放大，红框为实测可见像素 bbox，蓝框为 bubble Rect
- `after_virtual_drag_gray_1920x1080.png`、`after_virtual_drag_gray_zoom.png`：虚拟鼠标投喂后灰化状态

判定：修正前圆盘骑在描边上并露到玻璃门背景；修正后整个圆盘落在暖白内部，未覆盖描边、未接触尾巴，视觉居中，尺寸在 Uncle 小气泡内仍可清楚辨认。

## 七、自动化交互验证（隔离虚拟鼠标，未使用实体鼠标）

### 输入设备与注入方式

- 设备：Unity Input System 虚拟鼠标 `UncleDragVirtualMouse`，device id 21，`interfaceName` 为空；物理 RawInput Mouse id 2 未被注入事件、未被控制。
- 注入：仅用 `InputSystem.AddDevice<Mouse>()` + `InputSystem.QueueStateEvent(MouseState{position, buttons})`；`buttons=1` 表示左键按下，`buttons=0` 表示松开；12 步线性插值移动。
- 未调用 `mouse_event`、`SetCursorPos` 或任何 OS 级实体鼠标控制。
- 测试结束调用 `InputSystem.RemoveDevice()`；`Mouse.current` 回到物理设备 id 2。

### 实际经过的处理链路

虚拟 Mouse → `InputSystem` → `PointerSystem.Update()` → `HandleFrame()` → `PickDraggable()/BeginDrag()` → 每帧跟随指针 → `TryDrop()` → `DropZone.OnDrop()` → `GameManager.TryServeBowlDish()` → `DiningTable.ServeOne()`。

未直接调用 `ServeOne()`、`ManualTick()` 或任何业务接口来伪造上菜结果。备菜仅用 `FoodItem.Create` + `PutCookedDishInSlot` 将成品放入备菜槽，与既有验证口径一致。

### 结果

- 落点：备菜槽 `(780,161)`，Uncle 顾客 `(640,600)`
- 按下后：`dragging=True`，当前拖拽物 `dish_pepper_beef`
- 拖动中：物品位置随虚拟指针移动到 `(640,642)`
- 松开后：`dragging=False`
- Uncle：状态 `Waiting → Eating`，`served=0 → 1`，图标 `RGBA(1,1,1,1) → RGBA(0.50,0.50,0.50,1)`
- Boy：`served=00`，两枚图标仍为 `RGBA(1,1,1,1)`
- Girl：`served=000`，三枚图标仍为 `RGBA(1,1,1,1)`
- Console error：0

实体鼠标体验本轮不验收，留待正常游戏体验测试。

## 八、控制台与安全复核

- 视觉采集、边界测量、虚拟鼠标测试全过程 Console error 均为 0。
- Play Mode 已退出（`EditorApplication.isPlaying=False`）。
- 主仓库分支、HEAD、212 项未提交数量与三张素材 MD5 与开始时逐项一致。
- 未 reset / clean / stash / rebase；未提交或推送游戏主仓库；未推广到其他桌位；未继续 RiderB。

## 九、文件清单

- `report.md`（本文件）
- `layout_change.md`（参数前后对照与代码片段）
- `icon_visible_bounds.txt`（边界原始记录）
- `virtual_input_verification.txt`（虚拟输入证据摘要）
- `workspace_check.md`（工程基线复核）
- `before_single_dish_1920x1080.png` / `after_single_dish_1920x1080.png`
- `before_after_full.png` / `before_after_zoom.png` / `after_zoom_annotated.png`
- `after_virtual_drag_gray_1920x1080.png` / `after_virtual_drag_gray_zoom.png`
- `visual_capture_log.txt` / `virtual_input_log.txt`

**本轮到此停止，等待独立审阅。**
