# Restaurant Bubble Pilot — V2 候选图交接

本目录仅用于 **ChatGPT 独立视觉验收**：餐厅男孩桌气泡覆盖片 V2 候选图与其原始底图。
两张 PNG 均为原样复制，未压缩、未缩放、未调色、未修改任何像素。

## 文件清单

| 文件名 | 尺寸 | 用途 | 说明 |
|---|---:|---|---|
| `01_bubble_original_crop.png` | 343×204 | **原始底图** | 从原始餐厅背景 `restaurant_full.jpg` 的图像坐标 `(114,206)–(457,410)` 直接裁切。保留画死的两道静态菜（青椒炒肉、酸辣土豆丝）、完整双椭圆描边、尾部、阴影与背景。**这是未涂改的原始素材，仅作对照，不是候选成品。** |
| `bubble_boy_clean_v2_candidate.png` | 343×204 | **V2 候选图（待验收）** | 以上述原始底图为唯一修复源，清除气泡内部两道静态菜后得到的空白气泡覆盖片。保留气泡描边、尾部、阴影、气泡外背景与内部浅色底色；气泡外部与原始底图逐像素一致。 |

## 图片链接

- 原始底图（GitHub 页面）：https://github.com/Xyy5511122/cooking-review/blob/main/Restaurant_Visual_Reference/RestaurantBubblePilot_V2/01_bubble_original_crop.png
- 原始底图（Raw）：https://raw.githubusercontent.com/Xyy5511122/cooking-review/main/Restaurant_Visual_Reference/RestaurantBubblePilot_V2/01_bubble_original_crop.png
- V2 候选图（GitHub 页面）：https://github.com/Xyy5511122/cooking-review/blob/main/Restaurant_Visual_Reference/RestaurantBubblePilot_V2/bubble_boy_clean_v2_candidate.png
- V2 候选图（Raw）：https://raw.githubusercontent.com/Xyy5511122/cooking-review/main/Restaurant_Visual_Reference/RestaurantBubblePilot_V2/bubble_boy_clean_v2_candidate.png

## 验收要点（供参考，不作结论）

1. 气泡内部两道静态菜是否清除干净，有无菜品残影、盘缘弧线或色带。
2. 双椭圆描边、气泡尾部与阴影是否完整，有无被削弱或断口。
3. 气泡内部底色是否自然融合，有无矩形色块或明显色带。
4. 气泡外部背景是否与原始底图一致。

本轮仅作图片交接，**不对 V2 作最终质量验收**，等待独立审阅结论。
