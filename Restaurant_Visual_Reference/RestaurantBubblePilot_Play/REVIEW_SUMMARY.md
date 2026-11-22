# Restaurant Bubble Pilot B — 技术审阅摘要（Unity 单桌接入）

本目录发布的是第二阶段 B 的 **Unity Play Mode 实际运行证据**，供独立审阅。
本文件只包含文件/方法/行号/尺寸/哈希与结论记录，**不包含任何 C# 源代码、原始 diff、项目配置或无关文件**；源码继续保留在私有游戏仓库。

- 审阅阶段：第二阶段 B（index 0 左侧男孩桌单桌接入）
- 游戏分支：`refactor/data-driven-food`，HEAD `d2f0145`
- 发布仓库：`Xyy5511122/cooking-review`，目录 `Restaurant_Visual_Reference/RestaurantBubblePilot_Play/`
- 本轮状态：完成并停止，**未提交、未推送游戏源仓库，未推广到其他四桌**

---

## 1. 本轮修改的两个 C# 文件及涉及的方法

以下行号为当前工作区文件状态；SHA256 仅用于外部核对，**未上传文件内容**。

| 文件（私有仓库内路径） | 文件 SHA256 | 涉及方法 / 行号 | 改动摘要 |
|---|---|---|---|
| `Assets/Scripts/CookingDemo/UIBuilder.cs` | `0287041bba79bb19373ac42f0d2d1066c96a144a6560e6ec6a79e7541c4898db` | `BuildTable`（1344 行）；`index == 0` 守卫（1377 行）；覆盖片创建（1380–1383 行）；图标容器与 3 个图标槽（1385–1398 行）；引用注入（1509、1510、1524 行） | 仅在 `index == 0` 时创建 `OrderBubbleClean_0` 无菜品覆盖片、`OrderIcons_0` 容器和 3 个 `DishIcon_0_*` 图标槽，并把 `dishIcons` / `dishIconRoots` / `orderBubbleGo` 注入 `DiningTable`。其它四桌不创建这些对象，相关引用仍为空数组 / null。 |
| `Assets/Scripts/CookingDemo/DiningTable.cs` | `4bb7f5192c8b17fbc1b81c52ae0e5ef0e824eb5892f5790cd396ef723c1ca411` | `orderBubbleGo` 字段（78 行）；`BubbleIconFit`（111 行）与 `s_bubbleIconFits`（116 行）；`ArriveAs`（179 行，调用见 223 行）；`ServeOne`（271 行，灰化 280 行）；离场/清桌隐藏（317、332、359、423 行）；`BindBubbleIcons`（471 行）；`ApplyBubbleIconFit`（507 行）；`HideBubbleOrder`（544 行） | 新增覆盖片引用、四道菜 alpha 边界补偿表与绑定/尺寸/隐藏辅助方法；`ArriveAs` 按真实 `dishId` 调用 `RestaurantMenu.Find(id).icon` 绑定图标并显示覆盖片；`ServeOne` 只把对应已上菜品图标变灰；顾客离场与清桌路径统一隐藏覆盖片和图标，避免旧订单残留。 |

未修改文件：`GameManager.cs`、`RestaurantMenu.cs`、其它任何 C# 文件、任何既有素材或 `.meta`。

---

## 2. 覆盖片资源路径、尺寸与 SHA256

| 项目 | 值 |
|---|---|
| 游戏内正式资源路径 | `Assets/Resources/Art/Restaurant/bubble_boy_clean.png` |
| 来源（仅读取，未改动） | `cooking/ArtReview_Staging/RestaurantBubblePilot/02_bubble_clean.png`（第二阶段 A 已审阅素材） |
| 运行时加载键 | `Art/Restaurant/bubble_boy_clean` |
| 尺寸 | `343 × 204` 像素 |
| 文件大小 | `76,580` bytes |
| SHA256 | `a6ae4fa11d19944e049ab17e58b673c0db82912eb94c640d9ea1749ce10637c6` |
| 配套 `.meta` | 新建 GUID；`spriteMode: 1`、`spriteMeshType: 0`、`alignment: 0`、`spritePivot: (0.5, 0.5)`、`textureType: 8`、`spriteSheet` 矩形 `343 × 204` |
| 图片字节校验 | 与来源文件 SHA256 完全一致，未重新压缩、未改像素 |

覆盖片作用：盖住底图 `restaurant_full` 中烘焙的静态菜品，使气泡菜品完全由真实订单数据驱动；覆盖片与原图像素对齐，动态图标位于覆盖片之上。

---

## 3. 四种菜品的 RectTransform 尺寸与 Alpha 可见区域尺寸

Alpha 边界按 `alpha > 32` 程序化实测；`texture` 为源图边长，`center` 为可见中心（图像坐标）。
RectTransform 一律正方形，不拉伸、不裁剪、不修改原始 Sprite，并按可见中心做偏移补偿。

| 菜品 | dishId | 源图边长 | Alpha 可见包围盒 | Alpha 可见中心 | 3菜 RT / 可见 | 2菜 RT | 1菜 RT |
|---|---|---:|---:|---:|---:|---:|---:|
| 番茄炒蛋 | `dish_tomato_egg` | 1024 | `803 × 618` | `(501.5, 499)` | `117.3 × 117.3` / `92 × 70.8` | `158.1 × 158.1` | `188.7 × 188.7` |
| 青椒炒肉 | `dish_pepper_beef` | 1024 | `868 × 860` | `(512, 512)` | `108.5 × 108.5` / `92 × 91.2` | `146.3 × 146.3` | `174.6 × 174.6` |
| 土豆饼 | `dish_potato_cake` | 512 | `485 × 468` | `(256.5, 256)` | `97.1 × 97.1` / `92 × 88.8` | `130.9 × 130.9` | `156.2 × 156.2` |
| 酸辣土豆丝 | `dish_hot_sour_potato` | 512 | `486 × 473` | `(256, 255.5)` | `96.9 × 96.9` / `92 × 89.5` | `130.6 × 130.6` | `155.9 × 155.9` |

布局基准：1 / 2 / 3 菜可见目标宽分别为 `148 / 124 / 92 px`，间距 `0 / 18 / 6 px`，三图标整体居中且不超出气泡有效区域。运行时探针读回值与上表一致（例如三菜初始态：青椒炒肉 `108.5`、酸辣土豆丝 `96.9`、土豆饼 `97.1`；单菜番茄炒蛋 `188.7`）。

---

## 4. 八项 Play Mode 验收结果

全部为 Unity Play Mode 真实截图（原始分辨率 `1844 × 1037`），不是静态合成图。裁图为从对应原图截出的男孩气泡区域 `360 × 260`（原图 `(100,140)–(460,400)`），便于放大检查图标比例与灰化。

| # | 场景 | 结果 | 原始截图 | 局部裁图 |
|---|---|---|---|---|
| 1 | 单菜订单 | PASS | `bubble_b_01_single.png` | `crops/bubble_b_01_single_crop.png` |
| 2 | 双菜订单 | PASS | `bubble_b_02_two.png` | `crops/bubble_b_02_two_crop.png` |
| 3 | 三菜初始状态 | PASS | `bubble_b_03_three_initial.png` | `crops/bubble_b_03_three_initial_crop.png` |
| 4 | 三菜完成第一道菜 | PASS：仅第 1 道变灰 | `bubble_b_04_three_first_served.png` | `crops/bubble_b_04_three_first_served_crop.png` |
| 5 | 三菜完成第二道菜 | PASS：前 2 道变灰、第 3 道正常 | `bubble_b_04b_three_second_served.png` | `crops/bubble_b_04b_three_second_served_crop.png` |
| 6 | 三菜全部完成 | PASS：3 道全灰 | `bubble_b_05_three_all_served.png` | `crops/bubble_b_05_three_all_served_crop.png` |
| 7 | 顾客离场 | PASS：覆盖片与图标均隐藏，空桌干净 | `bubble_b_06_customer_left.png` | `crops/bubble_b_06_customer_left_crop.png` |
| 8 | 下一位顾客到达 | PASS：新订单为酸辣土豆丝 + 土豆饼，无上一位残留 | `bubble_b_07_next_customer.png` | `crops/bubble_b_07_next_customer_crop.png` |

运行探针回读（摘要）：单菜 `served=0`；三菜完成第一道 `served=100`（对应图标灰度 `0.5,0.5,0.5`）；完成第二道后前两道图标变灰、第三道保持正常（见第 5 项截图）；全部完成 `served=111`；下一位顾客 `served=00`，图标重新绑定新菜品。第 6 项截图捕获于全灰瞬间，随后实时计时自然推进到 `CoinAndTrash`（既有离场逻辑隐藏气泡），属正常时序推进，不是图标异常。

目视确认：底图静态菜品被完全覆盖；覆盖片与原图像素对齐；图标位于覆盖片之上；未被 mask / Cover / Toast 层级遮挡；空桌无图标或脏块残留。

---

## 5. DevSelfTest 结果

`DevSelfTest`：**307 PASS / 0 FAIL**（使用既有验证入口运行，与项目基线一致）。

---

## 6. 编译错误与 Console Error

- 编译错误：**0**
- Unity Console error：**0**（Play Mode 探针回读 `Retrieved 0 log entries.`）

---

## 7. 随机订单逻辑未修改的核对结果

- `GameManager.cs`、`RestaurantMenu.cs` 均**未修改**。
- `TrySpawnNextCustomer()` 仍按原座位规则调用 `RestaurantMenu.MakeOrder()`；堂食随机 2–3 菜、外卖 1 菜的规则不变。
- 为覆盖 1 / 2 / 3 菜场景，测试只是反复调用真实 `MakeOrder` API 直到取得目标菜数；代码中没有固定座位订单，也没有固定菜品组合。

---

## 8. 五张餐桌中仅 index 0 接入的核对结果

- `UIBuilder.BuildTable` 中新增对象全部位于 `if (index == 0)` 分支内（1377 行）。
- index 1–4 的 `dishIcons` / `dishIconRoots` 仍为 `new Image[0]` / `new GameObject[0]`，`orderBubbleGo` 为 null，未创建覆盖片或图标槽。
- 本轮只改动了 `Assets/Scripts/CookingDemo/UIBuilder.cs` 与 `Assets/Scripts/CookingDemo/DiningTable.cs`，以及新增一个覆盖片资源及其 `.meta`；其它四桌的代码、资源和截图表现未动。

---

## 9. 当前 Unity 工作区状态

- 分支：`refactor/data-driven-food`，HEAD `d2f0145`（`ahead 34, behind 6`）
- **未提交、未推送**：没有执行 `git commit` / `git push`，也没有 `reset` / `clean` / `stash`
- `git status --short | wc -l` 为 **210**；本轮变化为 2 个 C# 文件修改 + 2 个新增资源文件（`bubble_boy_clean.png` / `.meta`），新资源位于本就整体未跟踪的 `Assets/Resources/Art/Restaurant/` 目录内
- 公开审阅仓库的本次发布是独立新增目录，未修改任何既有审阅材料

---

## 专项说明：番茄炒蛋三菜态可见高度偏小

三菜态下番茄炒蛋的 Alpha 可见包围盒为 `803 × 618`（宽高比约 `1.30`），在统一 `92 px` 可见宽约束下，可见高度只有约 **`70.8 px`**；而青椒炒肉 / 土豆饼 / 酸辣土豆丝分别约 `91.2 / 88.8 / 89.5 px`。这是**源素材本身为横向椭圆**导致的材质比例差异，不是被压扁或裁剪：RectTransform 仍为正方形、未拉伸、未裁剪、未修改原 Sprite。

请独立审阅时特别关注这一项：`bubble_b_03_three_initial.png` / `crops/bubble_b_03_three_initial_crop.png` 中若出现番茄炒蛋，其观感会明显比另外两道菜矮；当前方案没有为了让图标变大而突破气泡有效边界。是否接受该观感，尚待审阅裁决；本轮不据此自行调整或推广。

---

发布后停止，等待独立审阅；未进入其他四桌的推广。
