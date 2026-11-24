# 上游 WITW+WITE v0.9.60 意大利战区基线审计报告

> 本文件由 `tools/analyze_upstream_italy.py` 自动从 `source/witw-wite-v0.9.60/data/*.json` 提炼生成，供人类与 AI 开发时速查。

## 1. 地图裁剪口径对比
- **全欧底图**：`378 × 355 = 134,190` 格
- **意大利战役大剧本** (`NW=[104, 208], SE=[176, 318]`): 有效范围 `X:[104..175]`, `Y:[208..317]` = `7,920` 格（削减 `94.10%`）
- **哈士奇西西里小剧本** (`NW=[118, 275], SE=[166, 314]`): 有效范围 `X:[118..165]`, `Y:[275..313]` = `1,872` 格（削减 `98.60%`）

## 2. 上游意大利胜利点目标（从 `victory-points.json` 提炼）
- 命中数量：**16** 座城市，上游基础分合计：**124**

| 城市 | ID | 坐标 (X, Y) | 上游基础分 | 备注 |
| --- | --- | --- | --- | --- |
| Rome | 545 | (137, 255) | 30 | previous28_added_objectives |
| Milan | 541 | (120, 227) | 16 | previous28_added_objectives |
| Naples | 533 | (147, 263) | 16 | previous28_added_objectives |
| Turin | 540 | (113, 230) | 6 | previous28_added_objectives |
| Genoa | 542 | (119, 235) | 6 | previous28_added_objectives |
| Venice | 678 | (136, 227) | 6 | previous28_added_objectives |
| Bologna | 613 | (131, 235) | 6 | previous28_added_objectives |
| Florence | 544 | (131, 240) | 6 | previous28_added_objectives |
| Palermo | 566 | (143, 286) | 4 | previous28_added_objectives |
| Messina | 558 | (155, 284) | 4 | previous28_added_objectives |
| Zagreb | 3467 | (153, 223) | 6 | previous28_added_objectives |
| Ljubljana | 3466 | (146, 222) | 4 | previous28_added_objectives |
| Sarajevo | 3469 | (166, 237) | 4 | previous28_added_objectives |
| Split | 3471 | (157, 241) | 4 | previous28_added_objectives |
| Mulhouse | 3649 | (112, 209) | 3 | revised52_industrial_objectives |
| Grenoble | 3613 | (104, 229) | 3 | revised52_industrial_objectives |

## 3. 哈士奇行动已验证坐标（`board_shape = 2` 按行奇偶错位）
- **曾踩坑内陆格**：`[149, 293]`（不要将其当作登陆海滩，仅作 `3/82nd` 空降目标）
- **修正后 TF81 海滩**：`[147, 293]`，出海格：`[147, 294]`

### 两栖登陆编组 (6 支)
| TF ID | 登陆目标 (X, Y) | 出海海格 (X, Y) |
| --- | --- | --- |
| 13055 | (146, 293) | (146, 294) |
| 13058 | (147, 293) | (147, 294) |
| 13061 | (149, 294) | (148, 295) |
| 13064 | (154, 296) | (154, 297) |
| 13067 | (154, 293) | (155, 293) |
| 13070 | (153, 295) | (154, 295) |

### 空降预案 (7 支分队)
| 单位 ID | 目标 (X, Y) | 支援 TF | 说明 |
| --- | --- | --- | --- |
| 11542 | (146, 292) | 13055 | Optional reserve plan; moved off the new TF81 beach |
| 11543 | (148, 293) | 13058 | Optional reserve plan |
| 11544 | (149, 293) | 13061 | Initial US505th combat-team abstraction; original inland Gela/Piano Lupo area |
| 11546 | (153, 294) | 13070 | Optional reserve plan |
| 11547 | (152, 295) | 13070 | Optional reserve plan; avoids Canadian commando landing space |
| 11548 | (154, 294) | 13067 | Ladbroke glider-assault abstraction |
| 11774 | (147, 292) | 13055 | Optional509th reserve plan; not a historical Husky drop |

## 4. 增援与后勤基线统计（注意统计口径）
- 上游地面增援总记录：`1010` 条；其中落点坐标直接位于意大利大剧本框内的有 `13` 条（哈士奇框内 `12` 条），另有 `8` 条关键词命中但初始落点在英国/北非外侧。
- 上游航空增援总记录：`198` 条；按地中海关键词匹配 `1` 条（实际按所在机场归属裁剪，详见 `tools/crop_csv.py`）。
- 轴心预备队调整中涉及意大利关键词/坐标的记录：`0` / `33` 条。
- 盟军人力拨款上游基线：首笔 `250,000`，全欧双线总计 `1,960,000`（纯意大利战役需缩放到约 25%~35%）。
