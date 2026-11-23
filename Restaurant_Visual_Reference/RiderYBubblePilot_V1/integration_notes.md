# RiderY(index2) Unity 接入说明

## 改动文件（仅两处脚本 + 一个新资源）
1. `Assets/Resources/Art/Restaurant/bubble_riderY_clean.png`（新增）
   - 由独立裁片 bg(795,340) 265×160 清理生成，MD5 `7aa672cf51db056f664cc26790db0a7e`
   - 接入后 Unity 生成同名 .meta，sprite 名 `bubble_riderY_clean`

2. `Assets/Scripts/CookingDemo/UIBuilder.cs`（气泡数组，index2 位）
   ```csharp
   string[] bubbleRes = { "bubble_boy_clean", "bubble_uncle_clean", "bubble_riderY_clean", "bubble_riderB_clean", "bubble_girl_clean" };
   float[] bubbleX = { 114f, 628f, 795f, 1038f, 1458f };
   float[] bubbleY = { 670f, 682f, 580f, 585f, 656f };
   float[] bubbleW = { 343f, 240f, 265f, 240f, 280f };
   float[] bubbleH = { 204f, 132f, 160f, 155f, 156f };
   ```
   - index2：x=795、y=1080-340-160=580、w=265、h=160（源图像素独立标定，与 RiderB 的 (1038,340) 240×155 不同）

3. `Assets/Scripts/CookingDemo/DiningTable.cs`（新增独立布局 + 绑定）
   ```csharp
   private static readonly BubbleIconLayout s_riderYBubbleLayout =
       new BubbleIconLayout { bubbleW = 265f, iconCy = 107f, visible1 = 68f, visible2 = 72f, visible3 = 56f, gap2 = 10f, gap3 = 5f };
   ...
   BubbleIconLayout lay = index == 4 ? s_girlBubbleLayout : (index == 1 ? s_uncleBubbleLayout :
       (index == 3 ? s_riderBBubbleLayout : (index == 2 ? s_riderYBubbleLayout : s_boyBubbleLayout)));
   ```
   - 独立参数：iconCy=107、visible1=68（Play 差分标定后，见 icon_visible_bounds.txt）
   - 骑手固定单菜，visible2/3/gap 仅在多菜时用，给保守值不影响本轮

## 未改动
- Boy/Girl/Uncle/RiderB 已验收布局与素材、公共默认值、图标系统（未重构）
- CanvasScaler、5:4 / 16:10 画幅适配（未处理）
- RiderB/RiderY 之外的桌位、RiderB/RiderY 的 RiderB 相关坐标
- 订单生成逻辑（沿用现有 ArriveAs / MakeOrder / TryServeBowlDish，未改）

## 订单类型确认（只读）
- RiderY = GuestKind.Takeout（外卖骑手），订单固定单菜：`RestaurantMenu.MakeOrder(takeout)` → count=1
- 投喂链路：玩家按 Q 打包外卖盒 → `PutCookedDishInSlot(it, dishId, true)` → 虚拟鼠标拖 slot 到骑手 customerRt
  → `PointerSystem` → `DropZone.OnDrop` → `TryServeBowlDish`（校验 kind=Takeout 匹配）→ `ServeOne`
  → `TakeoutServed()` 隐藏气泡、骑手 Leaving、收入 `RestaurantMenu.Price(dishId, true)`（半价）
- 未直接调用 ServeOne/ManualTick 改变订单状态。

## 虚拟输入
- 独立 InputSystem 虚拟 Mouse（非 RawInput、iface 空），设备名 RiderYDragVirtualMouse / IsoVirtualMouse / IncVirtualMouse
- `AddDevice<Mouse>` + `QueueStateEvent(MouseState{position,buttons})`，press/release 跨真实帧边沿（wasPressedThisFrame 边沿检测要求）
- 未使用、未控制实体鼠标。
