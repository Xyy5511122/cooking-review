# 证据索引：报告行号 → 文件路径与代码版本

本文件为归档辅助材料，**不改变报告原文的任何结论**。目的是让外部读者知道 `ENGINEERING_REVIEW_2026-11-19.md` 中每个行号引用指向哪个文件、对应哪一份代码。

## 版本基准

| 项 | 值 |
|---|---|
| 审查日期 | 2026-11-19 |
| 私有 Unity 仓库 | `E:/un/u/My project (1)`（源码未公开） |
| 分支 | `refactor/data-driven-food` |
| HEAD | `d2f014507388893dbcb053ae4929d81734efb8e6` |
| 工作区 | 208 项未提交改动（136 `??` + 72 `M`），归档时复核仍为 208 项 |

**关键限定**：报告中的行号对应的是上述**工作区文件**，不是干净 HEAD 的文件。干净 checkout 的 `d2f0145` 与这些行号可能有差异。

下表 SHA256 于归档时对同一工作区文件**只读计算**，用于固定报告行号所指的版本；原 Unity 工作区未发生任何写入。本仓库只保存路径、行数与哈希，**不保存源码内容**。

## 1. Unity 源码（`Assets/` 相对私有仓库根）

| 文件 | 行数 | SHA256（归档时只读） | 报告引用行号 / 用途 |
|---|---|---|---|
| `Assets/Scripts/CookingDemo/GameManager.cs` | 4411 | `50bec4e2d89cbaedd41b9336a71a79df7d735b91bb8df1e1db05dfe6acc8d54e` | §1 检查区段 L1~150、240~400、540~630、1510~1550、2120~2220、2280~2400、2506~2570、2985~3200、3405~3465；正文逐点引用 L245、270~275、284、328~345、395~429、401、419、563、568、577、584、590、615~628、1515~1546、1523、1529、2132、2152、2157、2162、2170、2176、2188~2201、2286~2390、2307、2311、2318、2346、2356、2361、2506~2567、3019、3062~3069、3094、3100~3103、3131、3137~3142、3139、3151、3157、3160 |
| `Assets/Scripts/CookingDemo/StirFryFlow.cs` | 1961 | `ef3e1306f31eff53a11723fa269f2202d61f85fdf8fe19e0ce4f63e88a64ebc4` | L1~230（Phase/字段/Update，含 L54/57/62/198/199/212/217~226）、240~385（TickPotato，含 L373）、580~855（Activate/OnFoodDropped/HandleQE，含 L600/739~762/773/775/832/871）、905~933（GripHandleHeld，含 L905~909）、1608~1660（装盘入槽，含 L1616~1621）、1878~1941（Reset）、1947~1961（TossPullState） |
| `Assets/Scripts/CookingDemo/DevSelfTest.cs` | 1727 | `d5a21026b5c4c41d7977b72f8063a802d69d0cd11ab1f920dfadc6aa449aa6e8` | L11~82（Running 生命周期，含 L15/50~82/52/77）、690~810、1260~1290、1597~1663（ArmFinale/StirToss/ResetGrill）；另 L675/712/719/729/924/997/1014/1195/1272~1279/1282/1606/1609/1642 |
| `Assets/Scripts/CookingDemo/FoodItem.cs` | 759 | `f4555f4ce42a56fd59aa5d306def55d90b2002b2b693db56de4821f0d7717924` | L709（fast 状态判断） |
| `Assets/Scripts/CookingDemo/UIBuilder.cs` | 1599 | `853cd05464c983da69d619195e4db1b78b4bfb05028cf051b68d1fbeb84c0d0d` | L50~54（依赖注入）、710~740（点击翻面土豆守卫，含 L722） |
| `Assets/Scripts/CookingDemo/DiningTable.cs` | 389 | `57110db43821bbbad11bc3876c34a1f1691b48972b002b0fdd9eb94ac6bc7afa` | L1~90（状态机/职责/洗牌袋，含 L37~73）、L308（GM 驱动计时） |
| `Assets/Scripts/CookingDemo/RestaurantMenu.cs` | 109 | `d0c0b621963c0ab94ce734b2294c896cce8851360957659aad4fa5dc785647c0` | 全文（纯定价/订单生成，无跨模块写状态） |
| `Assets/Scripts/CookingDemo/FoodType.cs` | 94 | `0862da7e3a094acc206961cbad41d050804701dd7c1e0d6429c878cf721316e1` | L44（`ReadyToFinish` 注释） |

## 2. 数据资产（相对私有仓库根）

| 文件 | 行数 | SHA256（归档时只读） | 报告引用内容 |
|---|---|---|---|
| `Assets/Resources/Foods/potato_shred.asset` | 48 | `fdaa1442e9d1058aed3b5fc226630468d242344a296d42443759663a85c76569` | 字段 `canGrill:1` / `needsFlip:1` / `grillResult: dish_potato_cake` / `toppingResult` 为空 / `waitForTopping:0`，见报告 §2 问题 4 |

## 3. 探针与工具（相对 `cooking/` 工作脚本区，非 Unity 仓库）

| 文件 | SHA256（归档时只读） | 报告引用位置 |
|---|---|---|
| `_stirfry_eq_probe.cs` | `564f40d6800773ee9b3fc5709d872de020a58186ba90a46bf98485a254359c04` | 全文读取；L27~33 直接设 `stirTestMode/StirFryActive/phase`，L31 反射写 `phase=Plating`，L94~104 恢复字段并 `sf.Reset()` |
| `_potato_flow_probe.cs` | `4063602eacb2a7463f05987ccfd1dc0b1e8d326b003e42bf1219f5b1796b7a80` | 全文读取；L65~92 调 `Activate()/OnFoodDropped()` 并写 `_oilCount`，L84/L90、L122~135 喂 y 序列，L137 写 `_potatoSwept=7f` |
| `_run_feedback_probes.py` | `24cfa2f9a77cc14f68505906441a03e576e5cbda7fda18b1c3336af8c92a7a3f` | 探针批次清单（10 条） |
| `_pour_realtime_probe.py` | `42cd242ea057547b3dce938ed8e3b1a9f38cc352aa6cfc6269c063d8c44324dd` | 跨帧 deltaTime 先例（§2 问题 6） |

依据文档 `cooking/工作总Review_2026-11-19.md` 的 §5 / §7 / §9 为审查输入，不是源码，未纳入哈希表。

## 4. 复核方式

```bash
# 报告原文哈希（应为 c64b123d...）
sha256sum Engineering_Review_2026-11-19/ENGINEERING_REVIEW_2026-11-19.md

# 私有工作区文件哈希示例（需在原工作区执行，本仓库不含源码）
git -C "E:/un/u/My project (1)" rev-parse HEAD
git -C "E:/un/u/My project (1)" status --short | wc -l
sha256sum "E:/un/u/My project (1)/Assets/Scripts/CookingDemo/GameManager.cs"
```

本轮**没有运行编译、DevSelfTest 或动态探针**。报告中的 "307 PASS" 是历史验证记录引述，不是本次实测结果。
