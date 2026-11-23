# RiderB(index3) Unity 接入说明

## 修改范围（仅 index3）
共修改 2 个 C# 文件 + 新增 1 张运行素材，均为 index3 独立条目。

### 1. `Assets/Scripts/CookingDemo/UIBuilder.cs`（BuildTable 内气泡数组）
```csharp
// RiderB(index3) 独立标定：源图像素 (1038,340) 240×155 → UI 左下角 y=1080-340-155=585。
string[] bubbleRes = { "bubble_boy_clean", "bubble_uncle_clean", null, "bubble_riderB_clean", "bubble_girl_clean" };
float[] bubbleX    = { 114f, 628f, 0f, 1038f, 1458f };
float[] bubbleY    = { 670f, 682f, 0f, 585f, 656f };
float[] bubbleW    = { 343f, 240f, 0f, 240f, 280f };
float[] bubbleH    = { 204f, 132f, 0f, 155f, 156f };
```
- 仅把 index3 从 null 改为独立资源与坐标；index0/1/2/4 原值未改（index2 RiderY 仍为 null，未推广）。

### 2. `Assets/Scripts/CookingDemo/DiningTable.cs`
新增独立布局（与 Boy/Girl/Uncle 参数互不复用）：
```csharp
private static readonly BubbleIconLayout s_riderBBubbleLayout =
    new BubbleIconLayout { bubbleW = 240f, iconCy = 80f, visible1 = 96f, visible2 = 84f, visible3 = 64f, gap2 = 12f, gap3 = 5f };
```
绑定选择加入 index3 分支：
```csharp
BubbleIconLayout lay = index == 4 ? s_girlBubbleLayout : (index == 1 ? s_uncleBubbleLayout : (index == 3 ? s_riderBBubbleLayout : s_boyBubbleLayout));
```
- 其余公共默认值、`s_bubbleIconFits`、`ApplyBubbleIconFit`、`BindBubbleIcons` 通用逻辑、`HideBubbleOrder`、`ServeOne`/`ManualTick` 均未改。
- 气泡覆盖片/图标槽与 `Cover_i` 同生命周期（到达显示、离场隐藏）由既有框架负责，未改。

### 3. 运行素材
- 新增 `Assets/Resources/Art/Restaurant/bubble_riderB_clean.png`（含 Unity 自动生成的 .meta）。
- 未改动 Boy V3 / Girl V2 / Uncle V1 三张 clean 素材。

## 骑手订单/状态事实（接入前确认，未预设与堂食相同）
- `GameManager.SpawnNextGuest`：index 2/3 固定为 `GuestKind.Takeout`，其余堂食。
- `RestaurantMenu.MakeOrder(takeout)`：`count = takeout ? 1 : Random.Range(2,4)` → **骑手固定单菜**。因此本轮只注入/验证单菜，`visible1=96` 是唯一实际使用值；visible2/3 仅为结构占位未实测。
- 送达链路：`TryServeBowlDish` 要求 `table.kind == (bs.takeoutDish ? Takeout : DineIn)`；外卖盒由 `PutCookedDishInSlot(..., true)` 打包。送达后 `ServeOne` 灰化图标，`TakeoutServed()` 使骑手离场并隐藏气泡，外卖半价入账。
- 这些流程均为既有实现，本轮未改业务逻辑。

## 未改项（明确）
- CanvasScaler / 参考分辨率 / match 值：未改。
- 5:4、16:10 画幅适配：未处理（本轮只验 1920×1080）。
- RiderY(index2)：未接入、未改、未推广。
- RiderB/RiderY 的 GuestPos/BarPos 等骑手坐标：未改。
- 未重构图标系统；未新增公共接口；未改其他桌位参数。
