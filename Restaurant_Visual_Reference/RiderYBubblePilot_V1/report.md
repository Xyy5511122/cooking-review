# RiderY(index2) 动态气泡 Pilot V1 报告

验证时间：2026-11-24；1920×1080 Play Mode；审阅目录 `Restaurant_Visual_Reference/RiderYBubblePilot_V1/`
本轮只做 RiderY，不推广全桌位、不重构。RiderY 是最后一个接入动态气泡的桌位。

---

## 一、基线（本轮实测，非历史）
- 主仓库 `refactor/data-driven-food`、HEAD `d2f0145`、212 项未提交；四张既有素材 MD5 与历史一致；审阅仓 `b7e0713` 干净。
- Unity Editor：bridge 可用、未播放、1920×1080。详见 `safety_review.md`。

## 二、阶段一：原始气泡诊断（只读）
- 历史 4x 裁片 FFT 模板匹配定位底图 **(795,340) 265×160**，MAE 0.923（极精确）。
- 椭圆主体 `x[816,994] y[351,438]`、中心≈(905,394)、rx≈89/ry≈44 —— **明显比 RiderB 更扁**（净高约70-84px vs RiderB 122px）。
- 尾巴：V 形折线朝下略偏右，尖端≈(918,471)；与黄色头盔前景基本不接触。
- **与 RiderB 的关键差异**（不可照搬）：
  - RiderY 顶部描边**独立干净**，不与门框连通（RiderB 顶部与门框竖条连通）；
  - 左侧门框竖杆 x≈785 与左描边有约 26px 间隙、不连通；
  - 右下无绿植遮挡（RiderB 右下被绿植挡）；
  - 左上角 x<845,y<360 是另一桌（Boy）气泡碎片，须保留。
- 故采用椭圆几何环 + 尾巴 V 多边形保护法，不依赖连通域。诊断报告与放大图见 `diagnosis_report.md` / `analysis/`。

## 三、阶段二：独立 clean 素材
- `bubble_riderY_clean.png`，265×160，RGB，MD5 `7aa672cf51db056f664cc26790db0a7e`。
- 改动 7457px（17.59%），改动 bbox bg `[828,363]..[981,427]` 全在气泡内部；**四边像素差异 0/0/0/0**（贴回无缝）。
- 暖白 guiding 逐行插值重建（顶带 y355-365 中位 (253,247,239)、底带 y428-434 中位 (252,243,234)）。
- 自检：4x/8x 交界放大（描边、V 尾、门框、头盔、另一气泡碎片）均无破坏；贴回 3x 无缝。详见 `material_spec.md` / `analysis/`。

## 四、阶段三：Unity 接入
- 仅改 `UIBuilder.cs`（气泡数组 index2）与 `DiningTable.cs`（新增 `s_riderYBubbleLayout` + index2 绑定）；新增一张 clean 资源。
- index2 独立坐标 x795/y580/w265/h160、独立布局 iconCy=107/visible1=68。
- 订单类型确认：RiderY = Takeout，固定单菜（`MakeOrder(takeout)` count=1），Q 打包→虚拟拖拽→`TryServeBowlDish`→`ServeOne`→`TakeoutServed`。详见 `integration_notes.md`。

## 五、阶段四：运行时验证（1920×1080 Play）
### A. 气泡显示 —— 已通过
- RiderY 到店显示 clean 气泡（sprite `bubble_riderY_clean`）；原背景静态四季豆炒肉菜品不再残留；
  暖白区完整；不遮挡描边、V 尾、门框、耐心条。五桌同营业截图见 `play_screenshots/`。

### B. 图标几何 —— 已通过（经一轮差分标定）
- 初次 visible1=84 → 可见像素 84×82，顶部压住上描边 2px；
- 标定后 visible1=68、iconCy=107 → 可见像素 **68×66（x894..961, y360..425）**：
  - 顶部退出描边约 7px、底部距描边 5px、距 V 尾尖 46px；
  - 完整落在暖白区、视觉居中、清晰可辨；
- 显示/隐藏差分证明只影响 RiderY 区域（其余四桌零像素变化）。详见 `icon_visible_bounds.txt`。

### C. 交互与状态 —— 已通过
- 独立虚拟 Mouse（id27/28/29、iface 空、非实体），press/release 跨真实帧边沿；
- 真实链路：PRESS→IsDragging=True/CurrentDrag=dish_potato_cake→拖动→RELEASE→DropZone→TryServeBowlDish→ServeOne；
- 结果：RiderY `Waiting→Leaving`、`served=1`、图标 `RGBA(0.5,0.5,0.5,1)` 灰化、气泡隐藏；
  **income 0→+8**（土豆饼原价16、外卖半价8）；未直接调用 ServeOne/ManualTick。
- 详见 `virtual_input_verification.txt` / `virtual_input_log.txt` / `income_log.txt` / 灰化截图。

### D. 并行营业隔离 —— 已通过
- Boy(0)+Uncle(1)+RiderY(2)+RiderB(3)+Girl(4) 同时营业；
- 投喂 RiderY 后 T0/T1/T3/T4 状态、served、图标颜色、气泡显示全部不变。详见 `isolation_log.txt`。

### Console Error
- 所有会话 `read_console(types=["error"])` = **0 条**。

---

## 六、结论分级
- **已通过**：原始诊断、独立 clean 素材（四边零差异）、Unity 接入、单菜显示、图标几何（含标定）、虚拟鼠标真实投喂/灰化/隐藏/收入、五桌隔离、Console 0 错误。
- **未通过**：无。
- **未验证**：实体鼠标真实拖拽手感（按要求未占用用户设备，留待正常游戏体验测试）；骑手耐心耗尽生气离场路径（本轮未触发）。
- **已知瑕疵**：气泡底部内缘一条淡盘缘阴影弧线（bg y≈423-427、x≈850-960，含少量绿/粉点，紧邻描边内缘）。该处原图盘缘几乎贴住描边、无干净暖白间隙，定点清除会产生锯齿或伤描边，按"优先保护描边与尾巴"原则保留，属天然内阴影级残留（与已验收 Uncle/RiderB 同类）；动态图标位于暖白中部，不受影响。
- **剩余风险**：无新增工程风险；主仓库改动均为预期接入，未提交。

## 七、结束后状态
- Play Mode 已退出；主仓库 HEAD `d2f0145`、未提交数守恒、四张既有素材 MD5 不变；无危险 Git 操作。
- 仅向 cooking-review 提交本独立目录，未提交主仓库。

**等待 ChatGPT 独立审阅。**
