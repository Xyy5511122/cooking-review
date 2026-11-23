# Uncle 独立布局参数改动

文件：`Assets/Scripts/CookingDemo/DiningTable.cs`

## 修改前

```csharp
// Uncle 单菜气泡 240×132，尾巴朝下偏左（自下而上 y<28）；图标中心放在 y=80 的暖白区，不压尾巴。
private static readonly BubbleIconLayout s_uncleBubbleLayout =
    new BubbleIconLayout { bubbleW = 240f, iconCy = 80f, visible1 = 112f, visible2 = 90f, visible3 = 68f, gap2 = 12f, gap3 = 5f };
```

## 修改后

```csharp
// Uncle 单菜气泡 240×132，尾巴朝下偏左；单菜可见像素实测 112×84 时会压住上描边，
// 故仅把 visible1 收到 72，并把 iconCy 上移 2px 到 82，使缩小后的图标落在暖白区中线。
private static readonly BubbleIconLayout s_uncleBubbleLayout =
    new BubbleIconLayout { bubbleW = 240f, iconCy = 82f, visible1 = 72f, visible2 = 90f, visible3 = 68f, gap2 = 12f, gap3 = 5f };
```

## 差异

| 字段 | 前 | 后 | 是否改动 |
|---|---:|---:|---|
| bubbleW | 240f | 240f | 否 |
| iconCy | 80f | 82f | 是 |
| visible1 | 112f | 72f | 是 |
| visible2 | 90f | 90f | 否 |
| visible3 | 68f | 68f | 否 |
| gap2 | 12f | 12f | 否 |
| gap3 | 5f | 5f | 否 |

绑定分支未改：

```csharp
BubbleIconLayout lay = index == 4 ? s_girlBubbleLayout : (index == 1 ? s_uncleBubbleLayout : s_boyBubbleLayout);
```

`ApplyBubbleIconFit()`、`s_bubbleIconFits`、`UIBuilder.cs`、`GameBootstrap.cs`、三张 PNG 素材均未改。
