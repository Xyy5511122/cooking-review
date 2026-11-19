# F-01 专项补充核查（勘误）

- 日期：2026-11-19
- 性质：对 `ENGINEERING_REVIEW_2026-11-19.md` 中 **F-01** 的补充核查与结论修订，并同步修正 **F-02** 的表述。
- 本文件是**追加勘误**，不是替换版。**原始报告一字未改**，其 SHA256 保持：
  ```
  c64b123da08b7dd0e51922e64c697bf22456e5556ca823dbdd96c337f5aa562d
  ```
  历史审查记录、风险等级表与结论均以原文为准；本文件只声明哪些结论经补充证据后需要下调。

## 0. 本轮边界（重要）

- **只读核查**：未修改任何 Unity 工程文件，未运行编译、DevSelfTest 或任何动态探针，未执行 Git 写操作于 Unity 仓库。
- **未做实测**：下文引用的静态检查与探针是**历史记录与代码事实**，不是本轮运行结果。不得据此声称"本轮实测通过"。
- **代码版本**：行号对应 `E:/un/u/My project (1)` 分支 `refactor/data-driven-food`、HEAD `d2f0145`、工作区 208 项未提交改动（136 未跟踪 + 72 已修改），归档时复核未变。
- **证据等级**：每条结论标注「已找到设计依据 / 仅从代码推断 / 尚无依据」；无明确记录处不反推设计意图。

---

## 1. 一次油 / 两次油的预期菜品：有明确设计依据

**结论：一次油 → 酸辣土豆丝；两次油（宽油）→ 土豆饼。**
证据等级：**已找到设计依据**（用户原话级，非代码反推）。

| 来源 | 路径与位置 | 内容 |
|---|---|---|
| 用户反馈原话要点 | `cooking/PENDING_ACCEPTANCE.md` §8.16，L647–648 | 「土豆丝放锅里以后系统强制转一圈做土豆饼，就做不了酸辣土豆丝了」。改成——**油壶放两次油（宽油）才走土豆饼；放一次油默认走常规炒（酸辣土豆丝）** |
| 改法记录 | 同文件 L651–657 | `IsWideOil` 定义；下锅 Toast「倒一次油＝常规炒，出锅是酸辣土豆丝」；阶段条文案随次数变化 |
| 后续修订 | 同文件 §8.17，L689–692 | 常规土豆丝须走完中火 Q/E 翻炒、小火调味、大火颠勺，最后出**酸辣土豆丝** |
| 历史实现记录 | `.workbuddy/memory/2026-11-19.md` L34 | 「油壶倒两次油＝宽油 → 土豆饼；倒一次 → 常规炒 → 酸辣土豆丝」 |
| 测试断言 | `cooking/_stirfry_static_check.py` L226–228 | 静态断言「宽油分流：倒两次油才进土豆饼，倒一次走常规炒（酸辣土豆丝）」 |

---

## 2. DevSelfTest 的 potato_shred 断言意图

**结论：验证的是旧通用烹饪流程的土豆饼（`NeedFlip → FlipPatty → grillResult`），没有声称覆盖玩家一次油流程。保留旧映射是有意设计，不是遗漏声明。**
证据等级：**已找到设计依据**。

| 位置 | 断言 |
|---|---|
| `Assets/Scripts/CookingDemo/DevSelfTest.cs` L289–296 | 切菜序列：土豆 → `potato_shred` |
| 同文件 L900–915 | 「出锅限制：土豆丝下锅」→ `FastGrill(..., NeedFlip, ...)` → `gm.FlipPatty(...)` → L907 断言 `dish_potato_cake` |
| 同文件 L1158–1187 | 「5. 土豆饼流程（含翻面）」→ `NeedFlip → FlipPatty → Done`，L1185 断言 `dish_potato_cake` |

全文检索 `hot_sour` / `OilCount` / `IsWideOil` / `StirFryActive = true` 在 `DevSelfTest.cs` 中**零命中**。

设计记录明确说明保留原因：`cooking/PENDING_ACCEPTANCE.md` L531「自测 `DevSelfTest.Running` 时全部放行旧路径，`potato_shred.asset` 的 `needsFlip/grillResult` 原值不动 → 307 保持」；L535「自测仍走旧映射 `dish_potato_cake`」。

因此 307 PASS 从未覆盖玩家油次流程；它验证的是旧映射土豆饼，这一点在设计记录中已写明。

---

## 3. `grillResult=dish_potato_cake` 的作用域与实际成品出口

**结论：`grillResult` 仅服务于旧通用烹饪流程；玩家两条路径的实际成品出口分别是 `L2199`（一次油）和 `L3141`（宽油）。**
证据等级：**已找到设计依据 + 代码调用事实**。

`Assets/Resources/Foods/potato_shred.asset`：L33 `needsFlip: 1`，L35 `grillResult` 指向 `dish_potato_cake`，L38 `toppingResult: {fileID: 0}`（空）。

代码的调用关系：

| 路径 | 入口与条件 | 成品出口 |
|---|---|---|
| 旧通用流程（自测） | `GameManager.AfterGenericStage2()` L3127 `result = d.grillResult`；L3131 的 `!Running && potato_shred` 覆写在自测中条件为假 | `grillResult` = `dish_potato_cake` |
| 玩家一次油 | `StirFryFlow.OnFoodDropped()` L739 的 `potatoShred && IsWideOil && !Running` 为假 → L764 `phase=Frying`；`GameManager.TickGenericCook()` L3062–3067 断生后置 `ReadyToFinish` 并 `return`；最终 `TryFinishDish()` L2196 取 `toppingResult`（空）→ L2199–2200 覆写 | **L2199–2200** → `dish_hot_sour_potato` |
| 玩家两次油（宽油） | `StirFryFlow.OnFoodDropped()` L739 条件为真 → `phase=PotatoSpread` → 中火两面煎制 → `GameManager.FinishPotatoCakeFromFlow()` | **L3141** → `dish_potato_cake` |

### 对原报告行的更正

- **L3062 不是成品映射**，而是状态挂起：它把 `it.state` 置为 `FoodState.ReadyToFinish` 后直接 `return`，作用是阻止旧计时器提前出菜，本身不决定成品 id。
- **L3131 不属于玩家一次油路径**：玩家侧在 `TickGenericCook()` L3062–3067 已提前返回，不会到达 `AfterGenericStage2()` 的 L3131。该覆写只在其他通用流程路径上可能执行。
- 原报告「三处映射各自硬编码（L2199 / L3062 / L3131）」的归纳应更正为：**玩家成品由 L2199（一次油）与 L3141（宽油）两处出口决定；L3062 是状态门禁，L3131 在玩家一次油路径上不可达**。

---

## 4. 是否存在真正的成品映射错误：分类结论

| 分类 | 结论 | 证据等级 |
|---|---|---|
| 设计明确要求但代码实现错误 | **没有找到**。三条路径成品均符合 §8.13 / §8.16 / §8.17 的明确设计：一次油出酸辣土豆丝、两次油出土豆饼、自测保留旧映射土豆饼 | 已找到设计依据 |
| 设计未明确、代码行为只是不同 | **没有找到**。常被误读的「自测出土豆饼」在 `PENDING_ACCEPTANCE.md` L531 / L535 有明确保留依据，不属于设计空白 | 已找到设计依据 |
| 测试覆盖不足，但成品结果本身符合设计 | **成立，且是本项的唯一真实风险**。`DevSelfTest` 无油次、无 `hot_sour` 断言；静态检查与探针另有覆盖，但均非真实鼠标/键盘端到端输入 | 已找到设计依据（测试文件）+ 代码事实 |

---

## 5. F-01 建议修订措辞

> **F-01｜自测与玩家成品路径分离（测试覆盖风险，非成品映射错误）**
> 事实：自测经旧通用流程出 `dish_potato_cake`；玩家一次油出 `dish_hot_sour_potato`（出口 `GameManager.cs:2199`），两次油（宽油）出 `dish_potato_cake`（出口 `GameManager.cs:3141`）。三者均符合 `PENDING_ACCEPTANCE.md` §8.13 / §8.16 / §8.17 的明确设计；自测保留旧映射是 L531 / L535 记录的保 307 有意安排，不是实现错误。`L3062` 是状态挂起而非成品映射，`L3131` 不在玩家一次油路径上。真实缺口：307 不覆盖玩家油次与一次油成品出口（`DevSelfTest.cs` 无 `OilCount` / `hot_sour` 断言）。
> **分类：测试覆盖不足；成品映射正确。等级：中（测试结构）。是否真实 Bug 风险：否。**

对应地，原报告 §6 风险表中 F-01 的「高 / 是——307 对玩家成品路径给出虚假通过」应下调为「**中 / 否（成品结果符合设计，缺口在测试覆盖）**」。

---

## 6. F-02 同步修正

原报告将玩家三阶段流程描述为「无自动化覆盖」，这不够准确。**新流程已有静态检查与状态探针，但没有形成真实鼠标、键盘输入的端到端自动化覆盖。**

> **F-02｜玩家新流程缺少真实输入的端到端自动化覆盖（测试覆盖风险）**
> 事实：`StirFryFlow.Update()` 在自测中因 `StirFryFlow.cs:199` 的 `stirTestMode` 短路，307 不驱动 Q/E 翻炒、拖油、调味、画圈与真实颠勺。但新流程并非完全没有测试：`_stirfry_static_check.py`（源码文本断言）、`_potato_flow_probe.cs`（油次分流与 phase 状态断言）、`_sour_flow_probe.cs`（常规流程推进与成品 id 断言）提供了覆盖。缺口在于这些是源码断言与反射写内部状态，**未覆盖真实鼠标拖拽 / 键盘按键到内部状态的完整链路**。
> **分类：端到端测试覆盖不足（非"完全没有测试"）。等级：中。是否真实 Bug 风险：否。**

---

## 7. 三类测试的覆盖边界（严格区分）

| 文件 | 覆盖内容 | 不覆盖 | 本轮是否运行 |
|---|---|---|---|
| `cooking/_stirfry_static_check.py` | **源码文本断言**：L226–228 检查 `IsWideOil` / `_oilCount` / `potatoShred && IsWideOil` 存在；L197–198 检查玩家侧不旧翻面与酸辣映射字符串 | 不执行游戏、不验证运行时状态机、不验证真实输入 | **否** |
| `cooking/_potato_flow_probe.cs` | Unity Play Mode 下通过反射写 `_oilCount`（L84/L90）、直接调 `Activate()` / `OnFoodDropped()`；L86 断言 `oil1 = !IsPotatoCakeMode && phase==Frying`，L92 断言 `oil2 = IsPotatoCakeMode && phase==PotatoSpread` | 不验证真实鼠标拖油壶入锅；不验证成品菜 id | **否** |
| `cooking/_sour_flow_probe.cs` | Play Mode 状态探针：L36 `frying`、L45 `ReadyToFinish`、L61 `dish_hot_sour_potato`、L102 汇总断言（历史记录 `frying/notDone/ready/keepFrying/season/readyToss/sour/plating`） | 反射直接设内部状态，不验证真实 Q/E 按键、鼠标拖拽、调味瓶拖放 | **否** |

上述覆盖情况来自文件读取与 `PENDING_ACCEPTANCE.md` §8.13 / §8.16 / §8.17 的历史验证记录。**本轮未运行任何一项**，因此本文件不提供新的 PASS 结论，也不改变历史 307 PASS 的性质。

---

## 8. 证据来源与验证边界汇总

- 设计文档：`cooking/PENDING_ACCEPTANCE.md` §8.13（L506–550）、§8.16（L645–668）、§8.17（L672–718），特别是 L531 / L535 / L647–648 / L689–692。
- 历史记录：`C:/Users/Administrator/WorkBuddy/2026-11-14-17-57-08/.workbuddy/memory/2026-11-19.md` L31–48、L50–72。
- 源码：`Assets/Scripts/CookingDemo/DevSelfTest.cs` L289–296 / L900–915 / L1158–1187；`StirFryFlow.cs` L199 / L732–735 / L739 / L764；`GameManager.cs` L2196–2202 / L3055–3067 / L3127–3133 / L3137–3142。
- 数据资产：`Assets/Resources/Foods/potato_shred.asset` L33 / L35 / L38。
- 测试文件：`_stirfry_static_check.py`（L197–198、L226–230）、`_potato_flow_probe.cs`（L81–93）、`_sour_flow_probe.cs`（L36–61、L102）。
- 验证边界：本轮为**只读静态核查**，未运行编译 / DevSelfTest / 探针，未做真实玩家操作。凡涉及运行时行为与实际观感的判断，仍待实机签核。
- 公开边界：本文件仅含勘误文本与引用；不含 Unity 源码、素材或项目文件。原 Unity 工作区 208 项状态未变。
