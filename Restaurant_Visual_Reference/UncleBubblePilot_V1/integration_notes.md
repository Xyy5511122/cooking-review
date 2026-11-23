# Uncle 气泡 V1 — Unity 集成说明

## 改动文件（仅 2 个 C# + 新增素材）
1. `Assets/Resources/Art/Restaurant/bubble_uncle_clean.png`（新增，MD5 `d95f53ae6bcc3641e81caa8547b0464d`）
   - 同目录另有 `bubble_uncle_original.png`（原始裁片，供对照，非运行必需）
2. `Assets/Scripts/CookingDemo/UIBuilder.cs` — `BuildTable` 气泡数组，仅填 index1：
   - `bubbleRes = { "bubble_boy_clean", "bubble_uncle_clean", null, null, "bubble_girl_clean" }`
   - 位置/尺寸：`bubbleX[1]=628, bubbleY[1]=682, bubbleW[1]=240, bubbleH[1]=132`
   - 复用既有"clean 覆盖片 + 3 个动态图标槽"创建逻辑（`hasBubble` 分支），无结构改动
3. `Assets/Scripts/CookingDemo/DiningTable.cs` — 新增独立布局并按 index 选用：
   - `s_uncleBubbleLayout = { bubbleW=240, iconCy=80, visible1=112, visible2=90, visible3=68, gap2=12, gap3=5 }`
   - `BindBubbleIcons()`：`lay = index==4 ? girl : (index==1 ? uncle : boy)`
   - 其余绑定/灰化/隐藏生命周期逻辑全部复用，未改

## 未改动（明确）
- 未改 CanvasScaler / 参考分辨率 / match 值；未处理 5:4、16:10 适配
- 未改 Boy(0)、Girl(4) 的素材、坐标、图标布局参数
- 未动 RiderY(2)、RiderB(3)（本轮不推广）
- 未改餐厅订单生成、送菜、耐心、金币等业务逻辑
- 未执行 reset / clean / stash / rebase；未提交或推送主仓库

## 独立参数说明
- 素材独立：Uncle 专属 clean PNG，非 Boy/Girl 素材复用
- 坐标独立：`bubbleX/Y/W/H[1]` 均为 Uncle 实测值，与 Boy/Girl 数组项不同
- 图标布局独立：`s_uncleBubbleLayout` 为中心/可见宽度/间距全套独立标定；单菜 bubbleW=240、iconCy=80（暖白区中心，避开下方尾巴 y<28）、visible1=112
