# Girl 气泡 V2 Unity Pilot 第二阶段：边界与真实操作验证

本轮只做验证，不新增功能、不修改美术素材、不扩展其他桌、不修改任何工程文件。
所有截图均为 Unity Editor Play Mode 真实运行画面，日志见 `run_log.txt`，工作区证据见 `workspace_check.txt`。

## 一、素材来源与本轮边界

- 使用素材：审阅仓库 commit `817394d` 中的 Girl V2 候选（工程内 MD5 `09eac2128e06c41c3152d8552a28bb52`）。
- Boy V3 保持原样（MD5 `197305afc71dad9f3ffb795942171024`）。
- 未修改 `UIBuilder.cs`、`DiningTable.cs`、PNG、`.meta`、订单逻辑、其他桌、Canvas Scaler 或锚点。
- 主仓库分支 `refactor/data-driven-food`、HEAD `d2f0145`、未提交改动 212 项，前后一致；未提交/推送主仓库。

## 二、已实际完成的测试（真实 Play Mode / 真实鼠标事件）

### 1. 三菜订单显示 —— 通过

- 截图：`three_dish_full.png`、`three_dish_bubble_zoom4x.png`
- 订单：番茄炒鸡蛋 / 青椒炒肉 / 酸辣土豆丝。
- 运行时读数：三个图标槽全部 active，sprite 分别为 `food_dish_tomato_egg`、`food_dish_pepper_beef`、`food_dish_hot_sour_potato`。
- 图标 rect（画布单位）：i0 pos=(61.0,86.8) 94.4²、i1 pos=(140.0,88.0) 87.3²、i2 pos=(220.0,87.9) 78.0²。
- 视觉检查：三个图标不重叠、不越过气泡左右边界、不压尾巴；原始两道静态菜品仍被完全覆盖；气泡轮廓/描边/尾巴完整；Console Error = 0。
- 订单设置使用运行时安全接口 `ArriveAs(...)`，未改正式订单生成逻辑。

### 2. 真实鼠标拖拽送菜 —— 通过

- 截图序列：`real_drag_01_before.png` → `real_drag_02_grabbed.png` → `real_drag_03_hover_girl.png` → `real_drag_04_served_gray.png`
- 使用 Windows 操作系统级鼠标事件（`mouse_event` 移动/按下/松开）驱动 Unity 新输入系统，**未调用 `ServeOne()`，也未调用 `PointerSystem.HandleFrame()` 代替交互**。
- 按下后运行时确认 `PointerSystem.IsDragging = true`，拖拽物为 `dish_tomato_egg`；悬停截图可见菜品被拖到 Girl 顾客附近。
- 松手后：`T4.served` 由 `000` 变为 `100`；第一个图标颜色由 `RGBA(1,1,1,1)` 变为 `RGBA(0.5,0.5,0.5,1)`；第二、第三个图标保持正常；Boy 桌与其他三桌状态未变。
- 重复送菜：`real_drag_05_repeat_rejected.png`。再次把同一道已送菜品真实拖给 Girl，状态保持 `100`，图标颜色不变，无异常 Toast 或 Console Error。
- 三道菜全部通过真实拖拽送达：`real_drag_06_first_served.png`、`real_drag_07_second_served.png`、`real_drag_08_third_served.png`；`T4.served` 依次为 `100` → `110` → `111`，三枚图标依次灰化，Boy 桌始终 `00`。
- 全部送达后：表进入 `Eating`，气泡与图标仍显示（因为测试冻结了时间）。随后用已有 `ManualTick(999f)` 两次推进用餐计时，状态进入 `CoinAndTrash`，`bubble=False`、`iconsActive=False`，截图 `real_drag_09_all_served_hidden.png`。**计时推进属于运行时接口模拟，不是真实等待。**

### 3. 不同分辨率 —— 部分通过，发现 1 个问题

- 截图：`resolution_1920x1080.png`、`resolution_1844x1037.png`、`resolution_1280x1024.png` 及各自气泡放大图。
- 1920x1080（16:9）与 1844x1037（上一轮使用的 16:9）：Girl 气泡、两个图标、耐心条、人物相对位置自然，无裁切、重叠或越界；Boy 桌正常。
- 1280x1024（5:4）：**发现右侧裁切**。Girl 气泡世界角点 x=1159..1382，屏幕宽仅 1280，右缘超出约 102px；耐心条同样被裁切。详见 `resolution_finding.txt`。按本轮要求只记录、未修复。
- Game View 尺寸通过编辑器反射接口临时切换，未修改 Canvas Scaler 或锚点。

### 4. Boy 与 Girl 同时营业 —— 通过

- 截图：`boy_girl_01_both_waiting.png`、`boy_girl_02_boy_served.png`、`boy_girl_03_both_served.png`
- T0（Boy）与 T4（Girl）同时为 `Waiting`，各自显示 2 个动态图标；T1/T2/T3 始终 `Empty`。
- 真实拖拽先送 Boy：`T0.served=10`（第一图标灰化、第二正常），`T4.served=00` 完全不变。
- 再真实拖拽送 Girl：`T4.served=10`（第一图标灰化、第二正常），`T0.served=10` 保持不变。
- 两桌气泡互不遮挡，其他三桌无变化，Console Error = 0。

## 三、通过运行时接口模拟或设置的部分（非真实玩家操作）

- 三菜/双菜订单通过 `ArriveAs(...)` 设置；未通过完整随机出餐流程触发。
- 测试菜品通过 `FoodItem.Create` + `PutCookedDishInSlot` 放入出餐槽；**从出餐槽到顾客的送达动作本身是真实鼠标拖拽**，但菜品的产生没有走完整厨房烹饪链。
- 时间冻结使用 `Time.timeScale = 0`；全部送达后的隐藏用 `ManualTick(999f)` 推进计时。
- 分辨率切换使用 GameView 反射接口，属于编辑器视图设置。
- `run_log.txt` 保留了完整过程，包括早期鼠标坐标校准失败、以及一次因测试脚本固定读取 0 号出餐槽而误拖到旧菜品的尝试；这些属于测试脚手架问题，已修正后重跑，最终证据以本 README 列出的截图与状态读数为准。

## 四、无法完成 / 未覆盖的测试

- 未做 Player Build，也未在真机或其他平台验证。
- 多分辨率测试只检查了静态布局（2 菜状态）；未在 1920x1080 / 1844x1037 / 1280x1024 下重复真实鼠标拖拽。
- 三菜订单只在 796x448 下做了显示验证，未在其他分辨率下验证三菜图标排布。
- 未模拟真实鼠标在 1280x1024 下点击被裁切区域；发现裁切后按停止条件未继续交互测试。

## 五、发现的问题

1. **1280x1024（5:4）右侧 Girl 气泡与耐心条被裁切**（约 102px）。运行时证据与归因见 `resolution_finding.txt`。归因指向工程现有 CanvasScaler 设置（参考 1920x1080、match 0.5），不是 Girl V2 素材或图标引入。未修复。
2. 测试过程中发现 `Mouse.current.position` 读数有约 1 秒延迟，真实拖拽需要等待事件落地后才能读到最终状态；这是测试环境观测延迟，不是游戏逻辑错误（最终状态与截图一致）。
3. Console Error 全程为 0，未发现新增异常。

## 六、结论与停止点

四项指定验证均已执行：三菜显示通过、真实鼠标拖拽送菜通过、多分辨率发现 1 项既有布局裁切、Boy+Girl 同时营业互不干扰通过。
本轮没有修改工程文件、没有替换素材、没有返修、没有推广到其他桌，也没有提交或推送主仓库。
按任务要求在此停止，等待 ChatGPT 独立审阅；5:4 裁切问题不自行修复。
