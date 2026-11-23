# Uncle 气泡 V1 补充验证报告（真实鼠标投喂 + 图标可见边界）

本任务是 Uncle V1 的补充验收，非返修。全程未修改任何 Unity 工程文件、C#、Prefab、素材或布局参数，未改变气泡实现，未提交/推送游戏主仓库。

## 结论速览

| 项 | 结论 |
|---|---|
| 验证 A：真实 OS 鼠标拖拽投喂 | **未通过（环境输入注入失败）**：OS 鼠标事件无法可靠驱动 Unity InputSystem，标定失败、按下未被识别、未发生拖拽。按约束未用模拟接口替代，相关功能项记「未验证」 |
| 验证 B：图标实际可见边界 | **已查明**：图标 Sprite 非透明像素真实越出气泡上缘（约 14px 相对 Rect / 约 21px 相对描边），圆盘骑在描边上并露出背景。非「透明边假象」 |

---

## 一、测试条件（实测，非推断）

- 分辨率：`SetCustomResolution(1920×1080)` 精确设定，运行时 `Screen=1920×1080`
- 画布：`Canvas.scaleFactor=1.000000`（1920×1080 为参考分辨率，1:1）
- Play Mode 已进入；Unity 6.4 (6000.4.7f1)；InputSystem Mouse id=2，interface=RawInput
- 起始基线：主仓库 `refactor/data-driven-food`、HEAD `d2f0145`、212 项未提交；Boy V3 `197305af`、Girl V2 `09eac212`、Uncle V1 `d95f53ae` MD5 未变
- 五桌到店：Uncle(index1) 单菜青椒炒肉；Boy(index0) 双菜；Girl(index4) 三菜

## 二、验证 A：真实 OS 鼠标拖拽 —— 未通过 / 未验证

### 执行过程
1. 将成品青椒炒肉放入备菜槽（`FoodItem.Create`+`PutCookedDishInSlot`，仅备菜，不代替上菜）。
2. 读运行时落点：备菜槽 `(330,203)`、Uncle 顾客 `(640,600)`。
3. 用真实 OS 鼠标事件（`mouse_event` 绝对/相对移动 + `SetCursorPos`）做闭环标定，逐步收敛到目标点。
4. 在备菜槽按下左键 → 分步拖向 Uncle → 松开。

### 实际结果（详见 runtime_log.txt）
- 标定 10 次迭代均失败：Unity `Mouse.position` 读数冻结在 `(870.03,92.23)` 与 `(1220.19,201.62)` 两个固定值间跳变，`Mouse.delta` 恒为 `(0,0)`。
- `left_down` 后 `PointerSystem.IsDragging=False`、`CurrentDrag=null` —— **按下未被游戏识别**。
- 因此未形成拖拽、未松手命中，未执行任何上菜。

### 根因定位（排除游戏逻辑问题）
- 已排除上轮 GameView 最大化因素：`GameView.maximized=False`。
- 焦点正常：`EditorWindow.focusedWindow = GameView`，前台窗口句柄为 Unity 主窗口 `0x10b8e`。
- 设备正常：Mouse id=2 / RawInput / `ProcessEventsInDynamicUpdate`。
- OS 层 `SetCursorPos` 能把物理光标放到指定点，但 Unity 收不到对应移动事件；相对事件的斜率测量自相矛盾（sx≈0、sy≈5），光标增量被系统抵消/吸附回原位。重启 Play 后复测仍跳变。
- 判定：这是**当前机器的输入注入环境问题**，与 Uncle 气泡实现无关。上一轮（Girl V2）同环境曾用真实鼠标成功，说明该环境不稳定、不可复现。

### 功能项状态（因拖拽未发生，全部「未验证」，不宣称通过）
- 鼠标按下/拖动/松开是否被识别：未验证（实测按下未识别）
- Uncle 菜品送达、图标灰化：未验证（served 前后均 `T1=0`，图标保持 white）
- Boy/Girl 图标不受影响：未验证（但状态前后一致，均 white，未见串扰）
- Console error：0（全程无错误）

### 结论
**验证 A 未通过**。按任务硬约束，未调用 `ServeOne()` / `ManualTick()` 或其他业务接口替代鼠标操作后冒充通过。`uncle_before_drag.jpg` / `uncle_after_drag.jpg` 为餐厅视图，画面一致（拖拽未发生）。

## 三、验证 B：图标实际可见边界 —— 已查明（越界）

### 数据口径（三层区分）
1. **RectTransform 边界**：icon `x 681.936..814.065, y 695.936..828.065`（左下原点，屏幕像素）
2. **Sprite alpha 边界**：源 PNG `alpha>32` 包围盒 `x 78..945, y 82..941`（1024×1024，图像坐标），与代码 `BubbleIconFit{alphaW=868, alphaH=860, cx=512, cy=512}` 一致
3. **最终可见像素**：经 `textureRect=(75.1,80,873.8,864.9)` 归一化后映射到 icon Rect，得 `x 682.4..813.6, y(bottom) 696.5..827.8`，即屏幕 `y 252.2..383.5`

### 对比（bubble Rect：x 628..868, y 682..814，屏幕 y 266..398）
- 可见顶部 `y=827.8` 比 bubble Rect 顶 `814` **高 13.8px**；比气泡椭圆描边顶（屏幕 y≈273）**高约 21px**
- 可见底部 `y=696.5`、左右 `682.4..813.6` 均在气泡内（左右各余约 54px）
- **不是**「Rect 超出但 Sprite 透明边缘未越界」的假象：源 PNG 在这 14px 范围内有真实 alpha 像素

### 像素证据（uncle_bubble_zoom.png 中央列 x=748，屏幕 y 自上向下）
| y | RGB | 内容 |
|---|---|---|
| 263 | (99,56,33) | 气泡描边暗棕 |
| 265 | (247,248,247) | 盘子白边（已在描边之上） |
| 281 | (70,154,61) | 青椒菜品 |

放大图直观显示：圆盘上半部越过气泡拱形描边、露在玻璃门背景上；**未压到下方尾巴**（尾巴位于气泡下方偏左，图标底边远高于它）。

### 判定
可见菜品**未**完全落在气泡内部，顶部真实越出约 14px（相对 Rect）/ 约 21px（相对描边）。此结论基于运行时数据 + 源 PNG alpha 扫描 + 截图像素三重核验，非肉眼印象。数据仅供审阅；本轮未改任何布局参数。

## 四、文件清单
- `report.md`（本文件）
- `runtime_log.txt`（真实鼠标事件与送菜状态）
- `uncle_before_drag.jpg`（1920×1080，餐厅视图，非空）
- `uncle_after_drag.jpg`（1920×1080，餐厅视图，非空；因拖拽未发生与 before 一致）
- `icon_visible_bounds.txt`（Sprite alpha 边界与最终可见范围）
- `uncle_bubble_zoom.png`（930×630，气泡局部 3× 放大，可看清图标与边界关系）

## 五、安全复核
- 未修改任何 Unity 工程文件/C#/Prefab/素材/布局参数；未改 CanvasScaler、坐标、画幅
- 未执行 reset / clean / stash / rebase；未提交或推送游戏主仓库
- 主仓库分支/HEAD/212 项未提交数量与开始时一致；三张素材 MD5 未变
- Play Mode 已退出；仅向 cooking-review 提交补充证据

## 六、事实 / 未验证 / 建议下一步
- **事实**：验证 B 已查明图标真实越界；验证 A 的环境输入注入在本会话不可靠
- **未验证**：真实鼠标拖拽的全部功能项（按下/拖动/松开识别、灰化、Boy/Girl 独立性）
- **建议下一步（供审阅决策，本轮不实施）**：若 ChatGPT 确认验证 B 的越界需修复，再单独立项调整 Uncle 的 `iconCy`/`visible1` 布局；真实鼠标验证建议在有稳定物理输入的机器上复测。不推广到 RiderB/RiderY。
