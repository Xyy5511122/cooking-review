# Girl 桌动态订单气泡 V2 — Unity 单桌 Pilot 运行预览

> 本目录只交付 Girl 桌（index 4）的 Unity 接入与真实 Play Mode 证据。尚未推广到 Uncle / RiderY / RiderB，未做五桌统一改造，等待 ChatGPT 独立审阅。

---

## 一、任务范围与素材来源

- 主仓库：`E:/un/u/My project (1)`（`Xyy5511122/cooking-roguelike-unity`），分支 `refactor/data-driven-food`，HEAD `d2f014507388893dbcb053ae4929d81734efb8e6`。
- 开始前未提交改动：212 项；结束后仍为 212 项（默认 `git status` 折叠既有未跟踪资源目录，文件级 mtime 复核确认仅 4 个 Assets 文件被触碰）。
- Girl V2 素材来源：`Xyy5511122/cooking-review` commit `817394d36f7035227708ed5c67761719de8499c2`，目录 `Restaurant_Visual_Reference/GirlBubblePilot_V2/`。
- 导入文件：`Assets/Resources/Art/Restaurant/bubble_girl_clean.png`，MD5 `09eac2128e06c41c3152d8552a28bb52`，与审阅 commit 中的候选逐字节一致；未重新生成或修改。
- Boy V3 MD5 前后均为 `197305afc71dad9f3ffb795942171024`，未触碰。
- 未执行 `git reset` / `clean` / `stash` / `rebase`；未提交或推送游戏主仓库。

---

## 二、实际改动

1. **素材**：新增 `bubble_girl_clean.png` + Unity 生成的 `.meta`（Sprite / Single / PPU 100 / 无 mipmap / Bilinear，与 Boy V3 导入规格一致）。
2. **UIBuilder.cs**：把 Phase B 从硬编码 index0 改为显式表，仅 index0 / index4 创建气泡和图标节点；Girl 坐标独立标定为源图 `(1458,268)` 280×156 → UI 左下 `(1458,656)`。Boy 参数原样保留，其他三桌仍不创建节点。
3. **DiningTable.cs**：新增 Boy / Girl 两套独立图标布局，仅 `BindBubbleIcons()` 读取布局；Boy 数值与修改前一致。Girl 使用气泡宽 280、图标中心 UI y=88、1/2/3 菜可见宽 116/100/74、间距 14/6。订单、送菜、灰化、耐心与隐藏逻辑均未改。

详细清单见 `targeted_changes.txt`，工作区复核见 `workspace_check.txt`。

---

## 三、已实际运行验证（Play Mode）

Unity Editor Play Mode，场景 `CookingGameDemo`，Game View `1844×1037`，`Time.timeScale=0` 冻结后执行。订单通过运行时调用 `DiningTable.ArriveAs(DineIn, 指定 dishId 列表)` 设置；这是只读运行态调用，没有修改正式订单生成逻辑。

| 项目 | 实际结果 | 证据 |
|---|---|---|
| Sprite 加载 | `sprite=bubble_girl_clean`，`rect=280x156` | `play_mode_log.txt` / `GIRL_ASSET` |
| 单菜订单 | `番茄炒鸡蛋¥18`；bubble=True；1 个图标，sprite=`food_dish_tomato_egg` | `girl_play_01_single_dish.png` |
| 双菜订单 | `番茄炒鸡蛋¥18  青椒炒肉¥28`；bubble=True；2 个图标，sprite 分别匹配 | `girl_play_02_double_dish.png` |
| 图标布局 | 单菜 pos≈(141.5,86.1) size≈147.9；双菜 pos≈(84.3,86.4)/(197.0,88.0)，size≈127.5/118.0；未重叠、未越界、未压尾巴 | `play_mode_log.txt` |
| 静态菜品清除 | 两张截图中 Girl 气泡内无原静态两道菜，只有动态图标；无静态+动态同时显示 | 01 / 02 截图 |
| 轮廓与右下过渡 | V2 描边、尾巴完整；3× 放大后右下浅灰过渡仍可见，但呈气泡自然阴影，不再呈盘缘弧线；实际游戏尺寸下不明显 | `girl_play_05_bubble_zoom_3x.png` |
| 送菜灰化 | `ServeOne("dish_tomato_egg")` 返回 True；i0 RGBA=(0.5,0.5,0.5,1)，i1 保持 (1,1,1,1) | `girl_play_03_served_gray.png` |
| 全部完成隐藏 | 两菜 ServeOne 后 `AllServed=True`；现有逻辑进入 Eating，再经 Leaving → `state=CoinAndTrash`，`bubble=False`、图标全 inactive | `girl_play_04_all_served_hidden.png` |
| 其他桌 | Boy T0 在进入测试前已由正常营业流程处于 Waiting 且 bubble=True、2 个图标，状态全程未被本次改动影响；T1/T2/T3 始终 Empty、无气泡/图标 | `play_mode_log.txt` 各 `TABLES_*` 行 |
| Console | Play Mode error 过滤返回 `Retrieved 0 log entries.`；无新增错误 | `console_result.txt` |
| 工程自检 | metaPairing / guidUnique / csharp 全部通过，0 error / 0 warning | `project_check.json` |

---

## 四、仅通过代码检查确认（未单独运行时断言）

- Boy index0 使用的 `bubble_boy_clean` 路径、气泡位置 `(114,670,343×204)` 与图标布局数值在本次修改前后完全一致。
- Boy V3 素材文件 MD5 未变；Boy 的动态图标与送菜代码路径未改。
- Uncle / RiderY / RiderB 仍走原静态背景流程：`bubbleRes[index] == null`，不创建覆盖片或图标节点。
- 新素材 `.meta` 为 Sprite/Single，GUID 唯一，PPU 100，与 Boy 导入设置一致。
- `BindBubbleIcons()` 的灰化、隐藏、订单文本、耐心条代码均未修改，Girl 复用既有生命周期。

---

## 五、尚未验证 / 风险

1. **单菜订单不是 Girl 自然生成路径**：`RestaurantMenu.MakeOrder(false)` 只生成 2–3 菜；单菜截图来自运行时安全调用 `ArriveAs(DineIn, 单菜列表)`，用于覆盖审阅要求的单菜边界，未改正式逻辑。
2. **送菜方式**：灰化通过已有公开接口 `ServeOne()` 触发，未模拟真实鼠标拖拽成品到 Girl 顾客；完整端到端拖拽链路未在本次逐帧验证。
3. **随机订单**：未等待随机订单自然命中 Girl，而是指定 `dish_tomato_egg` / `dish_pepper_beef` 以确保可复核；其他菜品图标在 Girl 气泡内的视觉表现未逐一截图。
4. **右下浅灰过渡**：在 3× 放大中仍可见一条极淡暖灰带，但不再呈盘缘形态；是否“完全自然”仍交由 ChatGPT 独立判断。
5. **编辑器与构建差异**：截图来自 Unity Editor Game View `1844×1037`，未做 Player Build；不同分辨率下的缩放未验证。
6. **Boy T0 状态**：全景截图中 Boy 桌处于 Waiting 是营业流程自然结果，不是 Girl Pilot 引入；Girl 测试没有修改它。

---

## 六、审阅材料索引

| 文件 | 说明 |
|---|---|
| `girl_play_01_single_dish.png` | Girl 单菜订单完整截图 |
| `girl_play_02_double_dish.png` | Girl 双菜订单完整截图 |
| `girl_play_03_served_gray.png` | 双菜中完成一道后的灰化截图 |
| `girl_play_04_all_served_hidden.png` | 全部完成后按既有逻辑隐藏气泡/图标 |
| `girl_play_05_bubble_zoom_3x.png` | 从双菜截图裁切的 3× 气泡放大，红框标出右下过渡 |
| `girl_play_06_restaurant_overview.png` | 餐厅全景（同双菜截图），可检查其他桌 |
| `play_mode_log.txt` | 运行时状态、图标 sprite / color / RectTransform 探针 |
| `console_result.txt` | Console 与工程自检结论 |
| `project_check.json` | unity-game-suite 离线自检 JSON |
| `workspace_check.txt` | 主仓库基线、MD5、改动文件清单 |
| `targeted_changes.txt` | 本轮最小代码/素材改动摘要 |
| `README.md` | 本报告 |

---

## 七、状态声明

- 本 Pilot 仅覆盖 Girl index4；未创建任何通用五桌改造；未改订单、顾客、耐心、送菜逻辑。
- 未修改 V1 / V2 素材审阅目录，未修改 Boy V3 审阅目录。
- 等待 ChatGPT 独立审阅；审阅通过前不推广到其他桌。
