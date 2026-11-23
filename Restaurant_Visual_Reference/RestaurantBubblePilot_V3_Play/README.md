# Restaurant Bubble Pilot — V3 Unity 单桌 Pilot 集成预览（等待独立审阅）

本目录记录：将 GitHub 审阅的 V3 候选图接入男孩桌（DiningTable index 0）后，在**真实 Unity Play Mode** 中的运行画面与验收结果。

**本轮不是正式验收通过**，仅供 ChatGPT 审阅实际游戏截图。

## 测试版本与素材

- 测试对象：男孩桌 index 0；其他四桌不改动。
- V3 来源：`Xyy5511122/cooking-review` → `Restaurant_Visual_Reference/RestaurantBubblePilot_V3/bubble_boy_clean_v3_candidate.png`，commit `9d75537`。
- 素材核对：从该 commit 下载 MD5 `197305afc71dad9f3ffb795942171024`，尺寸 `343×204` RGB，与接入工程内文件 MD5 一致。
- Unity 版本：`6000.4.7f1`（与工程 `ProjectVersion.txt` 一致）。
- 接入方式：仅替换 `Assets/Resources/Art/Restaurant/bubble_boy_clean.png` 的像素内容（代码通过 `Resources.Load<Sprite>("Art/Restaurant/bubble_boy_clean")` 加载）；`.meta` 导入设置未改（Sprite/Single/343×204/pivot 0.5/100px-per-unit）。未改任何 C#/场景/其他素材/动态图标实现/订单与送菜逻辑。
- 说明：此前工程内该路径实际是 V1 被破坏版（MD5 `e07a162a`，未导入 V2）。V2 仅为审阅候选。本轮是首次把通过审阅的候选接入工程，原文件已备份。

## 开始前状态（只读记录）

- 主仓库 `E:/un/u/My project (1)`：分支 `refactor/data-driven-food`，HEAD `d2f0145`，工作区 **212 项未提交改动**，未清理/回滚/stash/reset，未提交、未推送。
- 完成后工作区状态与开始前**逐行一致**（Play Mode 自动生成的 `_Recovery/0 (17).unity` 快照已备份并移除，不留在工程内）。

## 截图清单（均为真实 Play Mode 截图，非脚本合成）

| 文件 | 内容 |
|---|---|
| `v3_play_01_single_dish.png` | 男孩桌**单菜订单**完整游戏画面（1844×1037） |
| `v3_play_02_three_dish.png` | 男孩桌**三菜订单**完整游戏画面 |
| `v3_play_03_served_gray.png` | **送菜后图标灰化**完整游戏画面 |
| `v3_play_01_single_dish_zoom3x.png` | 单菜气泡区域 3× 放大（轮廓/尾巴/背景融合） |
| `v3_play_02_three_dish_zoom3x.png` | 三菜气泡区域 3× 放大 |
| `v3_play_03_served_gray_zoom3x.png` | 灰化气泡区域 3× 放大 |
| `play_mode_log.txt` | 运行期探针日志（状态/图标/颜色/其他桌/Console） |

放大图均从上述原始 Play Mode 截图裁切放大，未重绘、未改像素内容。

## 验收结果（自检，不作最终结论）

### A. 气泡覆盖效果
- V3 准确覆盖男孩桌原来画死的静态气泡菜品；单菜/三菜均只见动态图标，无静态菜残影。
- 外轮廓与原气泡对齐、平滑；尾巴位置与形状自然；无旧描边露出、无双层描边、无边缘错位。
- 气泡外背景无矩形色块或异常覆盖；底部阴影自然。
- 气泡内部暖白底色干净，无 R1/R2 盘缘暗弧残留（与 V3 静态验收一致）。

### B. 动态订单图标
- 单菜：1 个图标（`food_dish_tomato_egg`）；三菜：3 个图标正确显示，均完整位于气泡内部，未被覆盖片遮挡。
- 订单变化（单菜→三菜）时图标正确更新，尺寸/位置/层级与此前 Pilot 一致（148/124/92px 槽位）。
- 图标上可见的虚线圆环是动态焦点指示器：它在不同截图里环绕不同图标移动，位于覆盖片之上的动态图标层，静态 V3 PNG 不可能产生，属此前既有表现。

### C. 送菜状态
- 对 table 0 调用 `ServeOne("dish_tomato_egg")` 返回 true；对应图标颜色由 `RGBA(1,1,1,1)` 变为 `RGBA(0.5,0.5,0.5,1)`，另外两个保持正常色。
- 灰化只作用于菜品图标，气泡底色、描边、尾巴与背景未受影响。

### D. 稳定性
- **Console Error 数量：0**（`read_console` error 类型返回 0 条）。
- 其他四桌探针：T1–T4 均为 `Empty`、`bubble=null`，完全未受影响。
- 订单生成 (`RestaurantMenu.MakeOrder`) 与送菜 (`ServeOne`) 逻辑调用正常，未改动。

## 遗留问题 / 说明

- 本轮只验证了 index 0；未做完整流程（耐心耗尽、离场、外卖骑手等）的回归，按范围要求保持最小改动。
- 虚线焦点环为既有动态表现，非本轮引入；如需另行评估，属独立议题。
- 官方 Editor Play 截图分辨率为 1844×1037（Game 视图），放大图为裁切放大。
- 等待 ChatGPT 审阅实际截图，不自行宣布最终通过。
