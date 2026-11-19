# 工程审查报告（Engineering Review）

- 审查时间：2026-11-19
- 审查性质：**只读**。未修改、未提交、未 checkout/reset/clean/stash 任何文件。
- 审查依据：阶段性总结 `工作总Review_2026-11-19.md` 的 §5 / §7 / §9 所列风险点，但**所有结论均以真实源码、调用关系和实际 Git 状态为准**，不采信总结中的描述性文字。
- 报告独立性：本文件是唯一新建产物，位于 `cooking/` 工作脚本区（非 Unity 仓库内），不改变 307 PASS 基线。

---

## 0. 实际 Git 状态（现场核对，非沿用报告）

| 项 | 实际值 |
|---|---|
| 仓库 | `E:/un/u/My project (1)` |
| 分支 | `refactor/data-driven-food` |
| HEAD | `d2f0145` |
| `git status --short` 总数 | **208** |
| 其中 未跟踪 `??` | 136 |
| 其中 已修改 `M` | 72 |

与总结记录数字一致。审查过程未对上述状态做任何改动。

---

## 1. 实际检查的文件与模块

### Unity 源码（`Assets/Scripts/CookingDemo/`）

| 文件 | 行数 | 检查区段 |
|---|---|---|
| `GameManager.cs` | 4411 | 1~150（Update 输入分发）、240~400、540~630（流程开关/HandleChopKey）、1510~1550（门禁）、2120~2220（TryFinishDish/SettleToss）、2280~2400（火候/旋钮）、2506~2570（TryGrillDrop）、2985~3200（TickGrills/TickGenericCook/AfterGenericStage2/FinishGenericCook）、3405~3465（PutCookedDishInSlot） |
| `StirFryFlow.cs` | 1961 | 1~230（Phase 定义/字段/Update）、240~385（TickPotato）、580~855（Activate/OnFoodDropped/HandleQE）、905~933（GripHandleHeld）、1608~1660（装盘入槽）、1878~1941（Reset）、1947~1961（TossPullState） |
| `DevSelfTest.cs` | 1727 | 11~82（Running 生命周期）、690~810、1260~1290、1597~1663（ArmFinale/StirToss/ResetGrill） |
| `FoodItem.cs` | 759 | 709（fast 状态判断） |
| `UIBuilder.cs` | 1599 | 50~54（注入）、710~740（点击翻面土豆守卫） |
| `DiningTable.cs` | 389 | 1~90（状态机/职责/洗牌袋） |
| `RestaurantMenu.cs` | 109 | 全文 |
| `FoodType.cs` | — | 44（ReadyToFinish 注释） |

### 数据资产与探针（`Assets/Resources/`, `cooking/`）

- `Assets/Resources/Foods/potato_shred.asset`（核对 `needsFlip / toppingResult / grillResult`）
- `cooking/_stirfry_eq_probe.cs`（全文）、`cooking/_potato_flow_probe.cs`（全文）
- `cooking/_run_feedback_probes.py`（探针批次清单，10 条）
- 全局搜索：全 `CookingDemo` 目录无 `AudioSource/AudioClip/PlayOneShot` 命中。

---

## 2. 最高优先级：自测路径与玩家路径是否分离

### 结论先行

**是，两条路径在入口、状态写入、成品映射三个层面都实质性分离。** 307 PASS 无法证明玩家三阶段路径正确。这不是概括性判断，下面逐条给出调用链证据。

---

### 问题 1：玩家与 DevSelfTest 分别经过哪些入口、方法和状态分支？

#### 玩家路径（真实输入 → 状态机）

三个自动激活入口，全部在 `GameManager`：

| 触发 | 入口方法 | 关键守卫 | 结果 |
|---|---|---|---|
| 键盘 T 键 | `GameManager.Update()` L341~345 → `StartStirFryFlow()` L563 | 无守卫（玩家专用） | `Reset()`→`StirFryActive=true`→`Activate()` |
| 拧火到中火（直接档） | `SetGrillHeat()` L2289 → L2307 分支 | `h==Medium && !stirTestMode && (phase==Idle‖Done) && !HasDishInPan()` | `StirFryActive=true`→`Activate()` |
| 拧火到任意非空档（旋钮拖拽） | `Update()` L284 → `TickIgnitionKnobDrag()` L2318 → `SetKnobTowards()` L2346 → L2356 分支 | `!stirTestMode && !DevSelfTest.Running && grillHeat!=Off && !StirFryActive && (phase==Idle‖Done) && !HasDishInPan()` | 同上 |

玩家后续输入链：
- Q/E → `Update()` L328~335 → `HandleChopKey()` L584 → L590 `if (StirFryActive && _viewCook && !_viewRestaurant)` → `StirFryFlow.HandleQE()` L773。
- 真实鼠标拖锅柄 → `Update()` L270~275 → `TickWokHandle()` → `SettleToss()` L2132 → `TryFinishDish()` L2188。
- 拖拽倒油/调料 → `StirFryFlow.Update()` L212 `TickDrag()` → `CommitPour()`（L2527 门控只在 `TryGrillDrop` 侧）。
- 下锅 → `TryGrillDrop()` L2506 → L2567 `OnFoodDropped()`。
- 每帧推进 → `StirFryFlow.Update()` L217~221 `TickPotato()`（土豆专用）/ L223~226 常规动画。

**关键**：玩家路径里 `StirFryFlow.Update()` 是整套三阶段流程的驱动核心（拖拽、倒料、煎制计时、装盘动画都在这里 tick）。

#### 自测路径（脚本直接调方法 → 绕过 Update）

`DevSelfTest.Run()` L50~82：`Running=true` → `RunSteps()` → 逐个 `MoveNext()` → `Running=false`。

自测对火候/颠勺/状态的驱动方式：

| 自测动作 | 代码位置 | 与玩家的差异 |
|---|---|---|
| 设火候 | `SetGrillHeat(High/Low/Off)`，L675/719/729/924/1014/1195/1260/1282/1606 | **从未调用 `SetGrillHeat(Medium)`**（全文件搜索确认） |
| 设火候（旋钮） | `TickIgnitionKnobDrag()` L1272~1279，在 `stirTestMode=true` 下 | 走 L2346，但 L2356 被 `!stirTestMode` 挡住 |
| 颠勺 | `StirToss()` L1609：`stirTestMode=true` → 直接喂 `TickWokHandle` 坐标序列 → `TossTickGuide` | 绕过 `Update()` L270 的真实鼠标分支 |
| 强制成品时机 | `ArmFinale()` L1597：**直接写 `it.state = ReadyToFinish`**，`slot.stir.delay=0`，`SetGrillHeat(High)` | 完全跳过 QE 翻炒、调味阶段 |
| 强制收汁 | `FastGrill(..., ReadyToFinish, ...)` L712/997 等 | 直接把状态设到目标 |

**关键**：自测从不驱动 `StirFryFlow` 的三阶段（`Update()` L199 `if (... || gm.stirTestMode) { ... return; }` 直接短路）。自测走的是老引擎 `TickGenericCook`/`TickWokHandle`。

---

### 问题 2：哪些逻辑被 `stirTestMode` 或 `DevSelfTest.Running` 绕过？

按代码事实列出守卫清单（这是"三道守卫"的真实分布）：

| # | 位置 | 守卫表达式 | 被绕过的是玩家逻辑 |
|---|---|---|---|
| 1 | `StirFryFlow.cs:199` | `if (!cookView \|\| gm.stirTestMode) return` | 整个 `StirFryFlow.Update()`：拖拽、倒料、煎制、装盘动画、锅内图锚定 |
| 2 | `StirFryFlow.cs:600` | `if (gm==null \|\| gm.stirTestMode) return`（`Activate`） | 开锅初始化 |
| 3 | `StirFryFlow.cs:739` | `potatoShred && IsWideOil && !DevSelfTest.Running`（`OnFoodDropped`） | 土豆饼专用流程入口；自测恒走常规 Frying |
| 4 | `StirFryFlow.cs:775` | `if (gm==null \|\| gm.stirTestMode) return false`（`HandleQE`） | Q/E 翻炒与出锅分流 |
| 5 | `GameManager.cs:2307` | `h==Medium && !stirTestMode && ...`（`SetGrillHeat`） | **注意：此处没有 `!Running` 守卫**（见问题 3 分析） |
| 6 | `GameManager.cs:2356` | `!stirTestMode && !DevSelfTest.Running && ...`（`SetKnobTowards`） | 旋钮任意档自动激活 |
| 7 | `GameManager.cs:2515` | `!stirTestMode && !DevSelfTest.Running && !StirFryActive`（`TryGrillDrop`） | "没开锅不许下锅"的玩家门控 |
| 8 | `GameManager.cs:2527` | `StirFryActive && !stirTestMode && phase==Heating && !OilPoured`（`TryGrillDrop`） | "先倒油再下菜"的玩家门控 |
| 9 | `GameManager.cs:3062` | `!DevSelfTest.Running && d.id=="potato_shred"`（`TickGenericCook`） | 土豆丝挂起 ReadyToFinish（玩家）vs 旧翻面（自测） |
| 10 | `GameManager.cs:3064` | `if (StirFryActive && StirFry.IsPotatoCakeMode) return` | 土豆饼模式冻结旧计时器 |
| 11 | `GameManager.cs:3131` | `!DevSelfTest.Running && d.id=="potato_shred"`（`AfterGenericStage2`） | 土豆丝成品映射（酸辣 vs 土豆饼） |
| 12 | `GameManager.cs:3139` | `if (DevSelfTest.Running) return`（`FinishPotatoCakeFromFlow`） | 土豆饼专用收尾 |
| 13 | `GameManager.cs:2199` | `!DevSelfTest.Running && it.def.id=="potato_shred"`（`TryFinishDish`） | 颠勺成菜映射 |
| 14 | `UIBuilder.cs:722` | `!DevSelfTest.Running && def.id=="potato_shred"` | 点击翻面提示 |

**额外发现（守卫不完整）**：守卫 #5（`SetGrillHeat` 的 L2307 中火自动激活）**只有 `!stirTestMode`，没有 `!DevSelfTest.Running`**。若自测中在 `stirTestMode=false` 时调用 `SetGrillHeat(Medium)`，将触发真实 `Activate()`。当前 307 通过仅因自测从未调用 Medium——这是一处**脆弱的偶然安全**，而非稳固的设计隔离。（风险等级：中，见 §6 F-05）

---

### 问题 3：307 PASS 是否可能在玩家路径存在错误时仍然通过？

**可能，且是当前结构的必然属性。** 证据：

1. 玩家三阶段流程的驱动核心 `StirFryFlow.Update()` 在自测中因 L199 直接 return，**307 断言从未执行过** `TickDrag/TickPour/TickPotato/HandleQE` 的帧循环。
2. 玩家入口 `StartStirFryFlow()` / L2307 中火自动激活 / L2356 旋钮激活，三者在自测中要么不调用、要么被守卫挡掉。因此 **`StirFryActive` 在 307 全程基本为 false**（`devSelfTest` 中无 `StirFryActive = true` 的写入——全局搜索确认，仅 `GameManager` L568/L577/L2311/L2361 写入，前两处玩家入口自测不调，后两处被守卫挡）。
3. 成品映射分歧（见问题 4）：土豆丝在玩家侧与自测侧产出不同 `FoodDefinition`，307 只验证自测那一半。
4. 动态探针（10 条）是补充，但**探针本身也绕过真实输入**：`_stirfry_eq_probe.cs` L27~33 直接设 `stirTestMode=false`、`StirFryActive=true`、反射写 `phase`；`_potato_flow_probe.cs` L65~92 直接调 `Activate()`/`OnFoodDropped()` 并反射写 `_oilCount`。它们验证的是"给定内部状态时状态机正确"，不是"真实鼠标键盘能把内部状态推到那里"。

判定：**307 PASS = 旧引擎回归通过；玩家新流程正确性 = 未被 307 覆盖。** 二者不可互相替代。

---

### 问题 4：是否存在玩家路径与测试路径对同一食材产生不同状态结果？

**存在，且已定位到三处代码级分歧**，以 `potato_shred`（土豆丝）为最典型：

`potato_shred.asset` 实际字段：
```
canGrill: 1
needsFlip: 1
grillResult: {guid: eb54f77b...}   # 指向 dish_potato_cake
toppingResult: {fileID: 0}          # 空！
waitForTopping: 0
```

同一份土豆丝的三种结局：

| 场景 | 代码路径 | 结果 | 证据 |
|---|---|---|---|
| 自测（Running=true） | `TickGenericCook` L3062 条件为假 → 走 L3069 `NeedFlip` → 旧翻面 → `AfterGenericStage2` L3131 条件为假 → `result = d.grillResult` → `FinishGenericCook` | **`dish_potato_cake`** | L3062/L3131 + asset `grillResult` |
| 玩家·倒 1 次油 | `TickGenericCook` L3062 条件为真 → `state=ReadyToFinish` → 大火颠勺 → `TryFinishDish` L2199 条件为真 → `dish=dish_hot_sour_potato` → `FinishGenericCook` | **`dish_hot_sour_potato`** | L3062/L3065/L2199~2200 |
| 玩家·倒 2 次油（宽油） | `OnFoodDropped` L739 条件为真 → `_potatoCakeMode=true` → `PotatoSpread→Sear1→Flip→Sear2` → `FinishPotatoCakeFromFlow` L3137 → `dish_potato_cake` | **`dish_potato_cake`** | L739~762/L3137~3142 |

**已确认的事实**：自测跑出的土豆丝成品（`dish_potato_cake`）与玩家倒一次油跑出的成品（`dish_hot_sour_potato`）不是同一道菜。因此 307 中"土豆丝出菜"相关断言**验证的不是玩家常规路径的成品**。

附带观察（从代码推断，非断言失败）：`TryFinishDish` L2196 取 `dish = it.def.toppingResult`，而 `potato_shred.asset` 的 `toppingResult` 为 null；L2199 的 `!Running && potato_shred` 覆写是玩家侧能拿到酸辣土豆丝的唯一原因。这条覆写若被移除或条件写反，玩家侧会静默返回（`if (dish==null) return;` L2201），锅里的菜永远无法成菜。属于单点依赖。

---

### 问题 5：当前有哪些重要玩家操作没有被自动化测试覆盖？

按证据明确程度排序：

| 玩家操作 | 覆盖情况 | 依据 |
|---|---|---|
| 三阶段 QEQEQE 翻炒（按住锅把 + Q/E 交替） | **未覆盖** | `HandleQE` L832 `GripHandleHeld()` 依赖真实鼠标；307 中 Q/E 全走 `HandleChopKey` 切菜分支（L590 守卫在自测中 false） |
| 拖油壶入锅/悬停 0.55s 结算/油壶倾斜回弹 | **未覆盖** | `TickDrag`/`TickPour` 只在 `StirFryFlow.Update()` 里，自测 L199 短路 |
| 倒两次油→宽油计数 | 探针覆盖内部状态，非真实拖拽 | `_potato_flow_probe.cs` L84/L90 直接写 `_oilCount` |
| 土豆丝画圈平铺（306° 扫角） | 探针跳过真实输入 | `_potato_flow_probe.cs` L137 直接写 `_potatoSwept=7f` 跳过画圈 |
| 土豆饼颠勺手势（下拉→上推） | 纯逻辑探针覆盖，真实鼠标链路未覆盖 | `StepTossPull` 是静态纯逻辑，探针 L122~135 喂 y 序列；`GripHandleHeld` 的 `_gripLocked` 真实按下流程未测 |
| 出锅 E/Q 分流 + 三步打包 | 探针反射设 phase 覆盖状态机，真实按键未覆盖 | `_stirfry_eq_probe.cs` L31 反射写 `phase=Plating` |
| 场景切换（W/S/D）时流程恢复 | **未覆盖** | 见 §3 问题 3，`SetViewInternal` 无 `StirFry` 处理 |
| 玩家中火自动开锅（L2307/L2356） | **未覆盖**（自测无 Medium） | `DevSelfTest` 无 `SetGrillHeat(Medium)` |
| 调味 7 瓶拖入锅 | **未覆盖** | `CondimentBookkeeping` L881 只在 `StirFryFlow` 内部调用 |
| 餐厅上菜/耐心/收钱擦桌 | 部分探针覆盖状态，真实拖拽上菜未覆盖 | `_tray_probe` 类探针 |

---

### 问题 6：能否用现有动态探针/低成本方式验证真实玩家路径，而不破坏 307？

**可以，且现有工具链已具备全部要素，无需重构。** 证据与建议：

1. **已有独立场景复跑机制**：`cooking/_run_one_probe.py <探针名>`（见工作日志）会"重置场景 → Play → 执行"，探针通过反射读写，结束恢复原状态（`_stirfry_eq_probe.cs` L94~104 已完整示范恢复 `stirTestMode/StirFryActive/_viewCook/_viewRestaurant` 并 `sf.Reset()`）。因此新增探针不影响 307 的 307 条断言计数。
2. **307 与探针互不干扰的机制**：`DevSelfTest.Run()` 由 `SelfTestRequest.txt` 文件触发，`Running` 只在 [L52, L77] 之间为 true；探针在另一个 Play 会话里跑，不写该 flag。
3. **可低成本新增的探针类型**（均为反射/直接调方法，无需模拟真实 OS 输入）：
   - **入口守卫探针**：断言 `SetGrillHeat(Medium)` 在 `stirTestMode=false && phase==Idle && !HasDishInPan()` 下确实把 `StirFryActive` 置 true 且 `phase==Heating`（现无任何测试覆盖）。
   - **映射一致性探针**：对同一份 `potato_shred`，分别在 `Running=true`/`false` 下走 `AfterGenericStage2`，断言成品 id 差异符合设计意图——把"分歧"变成"显式契约"。
   - **场景切换探针**：在 `phase==Frying/PotatoSear1` 时调 `SetViewInternal(*,*)`，断言 phase 与锅状态不漂移。
   - **帧驱动探针**：用协程 yield 真实帧 + 反射喂鼠标坐标给 `TickDrag`/`GripHandleHeld` 依赖的坐标函数，覆盖 `StirFryFlow.Update()` 的帧循环（`_pour_realtime_probe.py` 已有跨帧 deltaTime 先例）。
4. **不破坏 307 的前提**：探针必须像 `_stirfry_eq_probe.cs` 那样在末尾恢复所有被改字段；不要在 `DevSelfTest` 内部加断言（那才会动 307）。

最小化建议：优先做 F-01/F-02 两个探针（成本最低、覆盖最大分歧），不改任何生产代码。

---

## 3. 第二优先级：新旧炒菜状态机并存风险

### 问题 1：新旧状态机是否仍可能同时推进同一个 FoodItem？

**存在明确的共享写入点。** `TickGenericCook`（旧）与 `TickPotato`（新）操作的是**同一个 `grillSlots[0].item`**：

- 旧：`GameManager.Update()` L245 `TickGrills()` → L3019 `TickGenericCook(it, slot)`，每帧读 `it.state` 并可能写 `NeedFlip/Melting/ReadyToFinish/Done`。
- 新：`StirFryFlow.Update()` L217~221 `TickPotato()`，土豆流程读 `_potatoTimer/_potatoSwept`，L373 调 `gm.FinishPotatoCakeFromFlow()` 间接写同一个 item。

两者靠**三处显式互斥**共存（已核实，不是靠巧合）：
- `GameManager.cs:3064`：`if (StirFryActive && StirFry.IsPotatoCakeMode) return;` —— 土豆饼模式下旧计时器 L3062 分支直接 return，不推进。
- `StirFryFlow.cs:739`：只有 `IsWideOil && !Running` 才进土豆专用，否则 phase=Frying 走常规。
- `GameManager.cs:3139`：`FinishPotatoCakeFromFlow` 在 Running 时 return。

**风险点（从代码推断）**：互斥依赖 `StirFryActive`、`IsPotatoCakeMode`、`DevSelfTest.Running` 三个外部状态同时正确。若任一在时序上不同步（例如 `EndStirFryFlow` L577 把 `StirFryActive` 置 false 时土豆流程尚未结束），互斥即失效。当前未在源码中发现会导致该不同步的具体玩家序列——**需真实操作验证**（见 §7）。

**已确认的一处设计限制**：`GameManager.cs:2400` 附近 `SetGrillHeat(h)` 被 `TickIgnitionKnobDrag`、自测、探针多处直接调用，而 L2307 的自动激活只在 `phase==Idle‖Done` 时生效；`phase` 在土豆流程中为 `PotatoSpread/Sear1/...`，因此中途拧火不会重开一锅（正确行为）。

---

### 问题 2：`ReadyToFinish` 是否存在无法结束、重复结算或提前完成路径？

**逐路径核对结果：**

| 风险 | 结论 | 证据 |
|---|---|---|
| 无法结束（卡死） | **有条件存在**。`ReadyToFinish` 在 `TickGenericCook` L3100~3103 明确"不再推进"，唯一出口是 `TryFinishDish` L2188，而后者要求 `grillHeat==High`（L2191）**且**一次接住成功（L2157/L2170）。若玩家始终不拧大火或颠勺总掉地上，状态会无限挂起。 | L2191~2195、L3100~3103、L1523 门禁禁止端走 |
| 提前完成 | 被 `BlockedPickup` L1529 + `TossBlocksTakeOut` L1515 挡住（`state==ReadyToFinish` 时禁止拾取），火候不足时 `TryFinishDish` L2191 拒绝。**代码层无提前完成漏洞。** | L1515~1546 |
| 重复结算 | **未见**。三处成菜出口互斥：`FinishGenericCook` L3151 立即写 `state=Done`；`TryFinishDish` L2190 开头检查 `state!=ReadyToFinish` return。土豆饼 L373 调 `FinishPotatoCakeFromFlow` 后 `phase` 随 `OnDishCooked` L676 变 `Plating`，不会二次调用。 | L2190/L3151/L676 |

**附带风险（中）**：`ReadyToFinish` 的"卡死"是设计选择（无倒计时，等待玩家操作），但缺少**退出通道**——玩家若把这道菜端不起来、又想重做，只能丢弃（`DestroyLostFood`）或靠 `ResetGrill`（仅自测用 L1642）。源码中未见玩家侧的"放弃当前挂起菜"入口。**需真实操作确认是否存在可恢复路径**（例如切场景/熄火后能否解除挂起）——从代码看 `SetGrillHeat(Off)` 并不清 `ReadyToFinish`。

---

### 问题 3：玩家中途取消、切换场景、重复触发入口时状态能否正确恢复？

**切换场景（已确认存在缺口）**：`GameManager.SetViewInternal()` L395~429 处理了打蛋取消（L401 `CancelEggCrackOnViewSwitch`）、三格槽位平移（L419），但**完全没有处理 `StirFryActive` 或 `StirFry.phase`**。

后果（从代码推断）：
- `StirFryFlow.Update()` L198 `cookView = gm.IsCookView && !gm.IsRestaurantView` → 切到餐厅后 L199~202 隐藏 UI 并 return，`phase` 原样保留。
- 切回烹饪画面时 `phase` 与 `_potatoTimer` 继续。对"煎制计时"而言，切走期间 `TickPotato` 不 tick，计时暂停——这是合理行为；但 `TickGrills()` 在 `Update()` L245 无条件每帧运行（注释明确"切到餐厅也不停止"），旧引擎继续推进锅里那份 item。
- **两者对同一 item 的推进节奏在切场景后分叉**：新流程暂停、旧引擎继续。土豆饼模式下旧引擎被 L3064 冻结（因 `IsPotatoCakeMode`），所以暂时安全；常规模式下若 item 处于 `Melting`，旧引擎会继续把它推到 `ReadyToFinish`（L3094），与新流程 phase 脱节。

**重复触发入口（部分防护）**：
- L2307/L2356 均有 `phase==Idle‖Done && !HasDishInPan()` 守卫，防止装盘后误重开。
- T 键 `StartStirFryFlow()` L563 无守卫，任意时刻按 T 都会 `Reset()`+`Activate()`——但 `Reset()` L1878 会 `ClearPlatedSource()` 销毁上一锅成品、清 `grillSlots` 占用吗？**不会**（`Reset` 只读 `grillSlots` 未写空）。因此中途按 T 会重置 phase 到 Heating，但锅里那份 item 仍是旧状态 → 新旧状态机对同一 item 认知不一致。**从代码推断存在风险，需真实操作验证**（探针可直接测：phase=Frying 时调 `StartStirFryFlow()`，断言 item.state）。

**中途取消**：源码中 `StirFryFlow` 无 Cancel 公共方法，只有 `Reset()`（L1878）。拖动倒料松手是 `GlideHome` 回位、不结算（`_pourDone` 防重复）——这一子是干净。

---

### 问题 4：是否存在状态机之间依靠多个布尔变量维持一致性的隐患？

**存在，且是本审查识别出的核心结构性隐患。** 维持一致性需要同时正确的布尔/枚举至少 6 个：

```
GameManager.StirFryActive          (L366)
GameManager.stirTestMode           (L1487)
DevSelfTest.Running                (static, DevSelfTest.cs:15)
StirFryFlow.phase                  (enum, 13 态)
StirFryFlow.IsPotatoCakeMode       (L62)
StirFryFlow.OilPoured / OilCount   (L54/57)
```

典型的一致性依赖链（土豆饼）：
```
倒油次数 OilCount>=2 → IsWideOil
   → OnFoodDropped 置 _potatoCakeMode=true (L741)
   → phase=PotatoSpread (L745)
   → TickGenericCook 靠 IsPotatoCakeMode 冻结 (L3064)
   → Sear2 结束靠 FinishPotatoCakeFromFlow 出菜 (L373)
   → FinishGenericCook 靠 StirFryActive 通知 OnDishCooked (L3160)
   → phase=Plating (L676)
```
任一环断裂的表现都是"流程卡住但无报错"——与历史教训中旧状态机静默跳过新流程的现象同源。

**判定**：这是真实的结构性风险（中），但**尚未发现当前代码里已触发的具体玩家序列**。属于"从代码推断的潜在维护风险"，不是已确认 Bug。

---

### 问题 5：当前方案能否继续维持，还是已出现实质问题？

**结论：可以继续维持，但有两个已确认的具体问题需要处理，其余是潜在/维护风险。**

已确认的实质问题（代码事实层面）：
1. **中火自动激活缺 Running 守卫**（F-05，见 §6）——守卫不完整，307 靠"自测不用中火"的偶然性维持。
2. **土豆丝成品映射分歧**（F-01）——自测与玩家产出不同菜，307 对玩家路径给出虚假安全感。

尚未发现实质 Bug 的方面：
- 新旧状态机对同一 item 的互斥在三处显式守卫下成立，未发现玩家序列能绕过。
- `ReadyToFinish` 的结束/重复结算路径完整（除"无退出通道"这一设计限制）。

不建议大规模重构——当前隔离方案在保 307 上有效，且代码量（StirFryFlow 1961 行）尚在可控范围。优先做"补齐守卫 + 加映射一致性探针"这类低成本改动。

---

## 4. 第三优先级：GameManager 职责与维护风险

### 职责耦合现状

`GameManager.cs` 4411 行，实际承担（从检查区段归纳）：

1. 主循环输入分发（Update L240~360：鼠标/键盘/W/S/D/QE/T/Tab）
2. 三阶段流程开关与转发（L563~591）
3. 拾取门禁/颠勺门禁（L1515~1546）
4. 颠勺物理与成菜判定（L2120~2220）
5. 火候旋钮/四档角度（L2286~2390）
6. 下锅/烹饪推进/旧状态机（L2506~2570, L2985~3161）
7. 三格槽位/出餐台/餐厅结算（L3405~3465）
8. 视图切换与 UI 平移（L395~465）

**跨模块直接修改内部状态的实例**（已确认）：
- `StirFryFlow.HidePlatedSource()` L1616~1621：直接写 `gm.grillSlots[i].item = null`，注释明确"不调用 GameManager.RemoveFromSource"。
- `StirFryFlow` 大量直接读写 `gm.ForceTossFocus`、`gm.SetPotatoTossGuide`、`gm.grillSlots[0].item`、`gm.stirTestMode`。
- `UIBuilder.cs:722`：在 UI 点击回调里直接判断 `DevSelfTest.Running` 和 `def.id=="potato_shred"` 并给业务提示——**UI 层混入了玩法规则**。
- `DiningTable.cs` 相对独立（状态机 + 耐心条 + 计时由 GM 驱动 L308），但持有 UI 引用（L37~73），属于"视图与逻辑同体"，与 `UIBuilder` 职责有重叠。
- `RestaurantMenu.cs`（109 行）职责最清晰：纯静态定价/订单生成，无跨模块写状态。

**判定**：`GameManager` 职责确实过重，但当前是"单体但有序"——各功能区有明确区段划分，没有出现互相踩踏的已确认 Bug。这属于**维护性风险（中）**，不是功能性风险。

### 新增音频系统的事件触发点（低成本建议）

全 `CookingDemo` 目录**无任何音频代码**（搜索 `AudioSource|AudioClip|PlayOneShot|.Play()` 零命中）。现有可复用的低耦合触发点：

| 触发点 | 文件:方法 | 触发时机 | 为何合适 |
|---|---|---|---|
| 切菜成功/切手 | `GameManager.HandleChopKey()` L615~628 | `ChopResult.Advanced/Completed/CutHand` | 已有明确分支，加一行 `AudioFeedback.Play()` 即可 |
| 颠勺接住/掉落 | `GameManager.SettleToss()` L2152/L2162/L2176 | Perfect/Good/失败三分支 | 三个声音状态天然区分 |
| 成菜 | `GameManager.FinishGenericCook()` L3157 | `PlayTransform` 旁 | 所有成菜路径（新旧状态机）都汇流于此 |
| 倒油/调料入锅 | `StirFryFlow.CommitCondimentDrag()` L871 / `CommitPour()` | 结算点 | 唯一结算入口，不会重复播 |
| 下单/上菜/收钱/顾客走 | `DiningTable` 状态切换（`ArriveAs`/`FinishWipe` 等） | 状态机转移处 | 集中在一处 |
| UI 通用提示 | `UIFeedback.Instance.Toast()` | 所有 Toast 调用点 | 可作兜底"提示音"，但会过密，建议只用于关键提示 |

最小化做法：新增一个 `AudioFeedback` 静态类（事件 → clip 映射），只在上述 6 处加调用，**不需要改 `GameManager` 的结构**。

### 低成本、低风险的模块化改进空间

1. **把守卫集中成属性**（不改行为）：在 `GameManager` 加 `PlayerInputActive => !stirTestMode && !DevSelfTest.Running`，替换 L2515/L2356 等重复表达式——减少 F-05 这类"漏写一个守卫"的错误。
2. **把土豆映射抽成单一函数**：`DishForPotatoShred(bool running, bool wideOil)`，让 L2199/L3062/L3131 三处调用同一函数，消除映射分歧（F-01）的根因。
3. **把 `UIBuilder.cs:722` 的业务提示移回 `GameManager`**（例如 `gm.FlipPattyChecked(it)`），UI 层只负责转发点击。

### 哪些是风格问题，哪些实际影响开发？

| 问题 | 分类 | 影响 |
|---|---|---|
| GameManager 4411 行单文件 | 风格/维护 | 增加定位成本，但不直接产生 Bug |
| 三处土豆映射各写各的 | **实际影响** | 已产生 F-01（自测/玩家成品分歧） |
| 守卫表达式重复且不一致 | **实际影响** | 已产生 F-05（漏写 Running） |
| UI 层写业务规则（UIBuilder L722） | 维护 | 规则改动需跨文件找，易漏 |
| DiningTable 持有 UI 引用 | 风格 | 当前无问题，继续加功能会加重 |

---

## 5. Git 与工程保护

- 实际状态见 §0：**208 项**（136 未跟踪 + 72 修改），分支 `refactor/data-driven-food`，HEAD `d2f0145`。
- 本审查**未执行** checkout / reset / clean / stash / commit / push，未修改任何 Unity 仓库文件。
- 唯一新建文件：`cooking/ENGINEERING_REVIEW_2026-11-19.md`（工作脚本区，非 Unity 仓库）。
- 208 项改动是本阶段工作累积，非本轮审查产生——已明确区分。
- 建议（不在本轮执行）：按模块分批提交（备菜美术 / 炒菜端 / 餐厅端 / 工具脚本），需用户明确授权。

---

## 6. 发现汇总与风险等级

| ID | 发现 | 分类 | 等级 | 是否真实 Bug 风险 |
|---|---|---|---|---|
| F-01 | 土豆丝在自测出 `dish_potato_cake`、玩家倒一次油出 `dish_hot_sour_potato`；三处映射各自硬编码（L2199/L3062/L3131） | 已确认（代码事实） | **高** | **是**——307 对玩家成品路径给出虚假通过 |
| F-02 | 307 全程不驱动 `StirFryFlow.Update()`；玩家三阶段（QE 翻炒/拖油/调味/画圈/颠勺真实输入）无自动化覆盖 | 已确认（代码事实） | **高** | **是**——玩家路径错误不会被 307 发现 |
| F-03 | `SetGrillHeat` L2307 中火自动激活缺 `!DevSelfTest.Running` 守卫，靠自测不用 Medium 的偶然性维持 | 已确认（代码事实） | **中** | 潜在——未来自测加中火用例会破坏 307 |
| F-04 | `SetViewInternal` L395~429 不处理 `StirFryActive/phase`，切场景后新流程暂停、旧 `TickGrills` 继续 | 已确认（代码事实）+ 后果推断 | **中** | 潜在——需真实操作验证是否造成卡死 |
| F-05 | 中途按 T 键 `StartStirFryFlow()` 无守卫，`Reset()` 不清锅里 item，phase 与 item.state 可能不一致 | 从代码推断 | **中** | 需验证 |
| F-06 | `ReadyToFinish` 无玩家侧退出通道，`SetGrillHeat(Off)` 不清该状态 | 从代码推断 | **中** | 需验证——可能"想重做却端不起来" |
| F-07 | 两个状态机共用 `grillSlots[0].item`，靠 6 个布尔/枚举维持一致性 | 已确认（结构） | **中** | 潜在——当前未发现触发序列 |
| F-08 | `TryFinishDish` 依赖 `potato_shred.toppingResult` 为 null 时的条件覆写，单点依赖 | 已确认（代码事实） | **低** | 否——当前正确，但脆弱 |
| F-09 | `UIBuilder.cs:722` 在 UI 层写玩法规则 | 已确认（代码事实） | **低** | 否——维护性 |
| F-10 | 全项目无音频系统 | 已确认（代码事实） | — | 否——需求空白，非缺陷 |
| F-11 | `GameManager` 4411 行职责过重 | 已确认（代码事实） | **低** | 否——维护性 |

**没有发现**以下严重问题：无编译期错误迹象、无明显的无限循环、无 `ReadyToFinish` 重复结算漏洞、无新旧状态机在当前代码中可直接触发的双写冲突。

---

## 7. 最小化建议（本轮不实施）

按"成本 / 收益"排序，全部不改 307 断言、不需重构：

1. **补 F-03 守卫**：在 `GameManager.cs:2307` 的 Medium 分支加 `&& !DevSelfTest.Running`，与 L2356 对齐。1 行改动，收益是消除偶然安全。
2. **加两个低成本探针**（不改生产代码）：
   - 入口守卫探针：验证 `SetGrillHeat(Medium)` 在玩家条件下确实激活新流程。
   - 映射一致性探针：把 F-01 的分歧变成显式契约（`Running=false` → hot_sour；`Running=true` → potato_cake），这样至少"已知分歧"被锁住，不会悄悄漂移。
3. **场景切换探针**（F-04）：在 `phase=Frying` 时切视图，断言 `phase` 与 `it.state` 不脱节。若失败，再考虑在 `SetViewInternal` 加处理。
4. **把三处土豆映射抽成单一函数**（F-01/F-08 的根因）：`DishForPotato(bool running, bool wideOil)`，L2199/L3062/L3131 统一调用。改动小，但需重跑 307 + 全部探针。
5. **可选**：加 `AudioFeedback` 静态类，按 §4 表格的 6 个触发点接入。
6. **不建议**：现在就拆分 GameManager 或合并两套状态机——收益低于风险，且 307 基线会受冲击。

---

## 8. 证据不足、需进一步验证的问题

以下问题**本报告不下定论**，因为静态代码审查无法覆盖运行时时序与真实输入：

1. **F-04/F-05 的真实触发序列**：切到餐厅再切回、或中途按 T，是否真的造成锅状态与 phase 分叉、菜卡死或重复。需真实玩家操作或专门的时序探针。
2. **F-06 的可恢复性**：玩家面对一份 `ReadyToFinish` 挂起的菜，是否存在"放弃重做"的合法操作（丢弃区是否接受、是否能用其他食材盖掉）。
3. **`_gripLocked` 的真实手感**：代码逻辑（L905~909 按下锁定、松手解锁）在真实鼠标事件顺序下是否与探针喂的坐标序列一致，尤其与 `TickWokHandle` 的锅把命中区叠加时。
4. **观感层面**：所有贴图位置、坐位、颠勺飞行高度、倒料速度——源码只能验证"接线正确"，不能验证"看起来对"。
5. **208 项改动的整体回归**：本轮只做了代码审查，**没有运行编译/DevSelfTest/探针**。"307 PASS"是沿用历史验证记录，非本轮实测。若需要，应单独跑一次 `python t2_verify.py`（在 cooking 目录）以确认当前工作区状态。

---

## 9. 审查声明

- 本轮严格只读：未修改任何 Unity 工程文件，未改变任何断言，未执行 Git 写操作。
- 所有"已确认"结论均给出文件路径 + 行号 + 方法名 + 条件分支；所有"推断"结论均标注了所依赖的假设。
- 报告本身是新产物，位于 `cooking/`（非 Unity 仓库），不会进入那 208 项待提交改动。
