# Restaurant Bubble Pilot B — Play Mode 运行证据索引

本目录发布第二阶段 B（Unity 单桌动态订单气泡 Pilot）的**实际运行截图**与审阅报告。
所有 `bubble_b_*.png` 均为 Unity Play Mode 真实截图，**原始分辨率 `1844 × 1037`，未二次压缩，不是静态合成图**。
`crops/` 下为从对应原图截出的男孩气泡局部（`360 × 260`，原图区域 `(100,140)–(460,400)`），仅用于放大检查图标比例与逐道灰化效果，原图同时保留。

技术结论、改动摘要、尺寸表与工作区状态见 [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md)。
**本目录不上传任何 C# 源代码、原始 diff、项目配置或无关文件；源码保留在私有游戏仓库。**

## 原始截图（Unity Play Mode，1844 × 1037）

| 文件名 | 测试场景 | 原始大小 | SHA256 |
|---|---|---:|---|
| `bubble_b_01_single.png` | 单菜订单：男孩气泡仅显示 1 道番茄炒蛋 | 2,187,654 | `f4271ec4191d01b5d0883b84d604f0e1efaa6bfcebbd3448f63dc7445bef5bd2` |
| `bubble_b_02_two.png` | 双菜订单：番茄炒蛋 + 土豆饼 | 2,226,693 | `ed2ec48e5d5e6d17c0de67649428895091b103a7bd82c143a7a60a8dcf3f303b` |
| `bubble_b_03_three_initial.png` | 三菜初始状态：青椒炒肉 + 酸辣土豆丝 + 土豆饼 | 2,225,625 | `3e51b41e37363177c52ab824c2b50c60874b50566915039ccfb9b80c5e3bc331` |
| `bubble_b_04_three_first_served.png` | 三菜完成第一道菜：仅第 1 道变灰 | 2,305,033 | `cf724d69090bc8532ff755804fba30616958ae531e54ba87b62cb9251a232d47` |
| `bubble_b_04b_three_second_served.png` | 三菜完成第二道菜：前 2 道变灰、第 3 道正常 | 2,199,242 | `a7817360570e5afb7953ccc180750dc60a349b0445a89b53ae41d7bca23ab39b` |
| `bubble_b_05_three_all_served.png` | 三菜全部完成：3 道全灰 | 2,338,987 | `49a0d25f09ad2b237ea212e459e4811088dcfe9d6b258ed11afb7f203f55d38b` |
| `bubble_b_06_customer_left.png` | 顾客离场：气泡覆盖片与图标隐藏，空桌干净 | 2,394,941 | `48af54b39eda6162af2fa3139aecabcd5d5cf0ab456bb99da11f00bbe082a238` |
| `bubble_b_07_next_customer.png` | 下一位顾客到达：新订单为酸辣土豆丝 + 土豆饼，无上一位残留 | 2,441,584 | `a6e7e95526e3a9ac669d4dfbd33d8360a0867afcaa7e29ee76c11868553ea02a` |

## 气泡局部裁图（360 × 260，与上表一一对应）

| 文件名 | 对应场景 | 原始大小 | SHA256 |
|---|---|---:|---|
| `crops/bubble_b_01_single_crop.png` | 单菜订单 | 156,118 | `44530e5482bf977bd764175a4d7aeb3d3fdf8e9004a7aa88b05b5c96754c4c9b` |
| `crops/bubble_b_02_two_crop.png` | 双菜订单 | 173,932 | `250589cb99810d9cc44a5d34003c4909f1a8800631a7db89a1a13657160d71d6` |
| `crops/bubble_b_03_three_initial_crop.png` | 三菜初始状态 | 170,883 | `288c0db4b067fece657f1987be40984e7de27e44d6c929a2a43bc07add7171e4` |
| `crops/bubble_b_04_three_first_served_crop.png` | 完成第一道菜 | 170,500 | `47b80459dfbef49c1bb8991dd7b78c0ceb82bc20012d222b3ad97ee384383df5` |
| `crops/bubble_b_04b_three_second_served_crop.png` | 完成第二道菜 | 167,872 | `9a141d91811b78b424c6d530e314b518344597f5c29558627844e7ffc4555606` |
| `crops/bubble_b_05_three_all_served_crop.png` | 三菜全部完成 | 171,975 | `f9ff9237253b1d768ef330c27c695321521b931ded9eee94edc4d69c523df816` |
| `crops/bubble_b_06_customer_left_crop.png` | 顾客离场 | 188,875 | `15d195e7a6eeda0fc0eba09e0d2e442de5798b75fa8448d9d3742ed4fff09269` |
| `crops/bubble_b_07_next_customer_crop.png` | 下一位顾客到达 | 178,531 | `4a76dd5906895532db9d384f8cd6d7f6ed2100ebfa1844697c7b3cf2d036b32a` |

## 审阅报告

- `REVIEW_SUMMARY.md` — 两个 C# 文件的改动方法/行号/文件哈希、覆盖片资源与 SHA256、四种菜品的 RectTransform 与 Alpha 可见尺寸、八项验收结果、自检与编译状态、随机订单未改核对、仅 index 0 接入核对、工作区未提交状态，以及番茄炒蛋三菜态可见高度偏小的专项说明。

本轮发布完成后停止，等待独立审阅；未推广到其他四张餐桌。
