# CSV 裁剪审计报告 — `italy_husky_43`

- **CSV 格式**：`new`
- **来源标识**：`WITW+WITE v0.9.60`
- **Dry Run**：`False`
- **有效坐标盒**：`NW=[57, 270]`, `SE=[166, 314]`（排除区 `1` 个）

## 实体裁剪统计
- **保留单位**：`433`（含机场 `60`）
- **停用/置空框外单位**：`10029`
- **保留航空队**：`159`
- **停用/置空框外航空队**：`2000`
- **框内城市**：`129`（其中港口 `25` 座）
- **已清零经济/补给的框外城市**：`3924`
- **清理残留 TB / Lock 字段**：`1`
- **活跃事件保留 / 停用**：`174` / `15`

## 需迁移或已自动迁移的祖先 HQ（共 11 个）
| Unit ID | 名称 | Player | 原坐标 | 建议锚点坐标 |
| --- | --- | --- | --- | --- |
| 11422 | USSTAF | 2 | [80, 176] | [126, 297] |
| 2 | OKL | 1 | [135, 180] | [156, 285] |
| 3236 | Italian High Command | 1 | [137, 255] | [156, 285] |
| 3280 | XXXI | 1 | [155, 269] | [156, 285] |
| 3250 | 7th | 1 | [155, 264] | [156, 285] |
| 11418 | SHAEF | 2 | [80, 176] | [126, 297] |
| 11421 | RAF HQ | 2 | [82, 176] | [126, 297] |
| 3240 | Army Group C | 1 | [138, 256] | [156, 285] |
| 2000 | OKW | 1 | [139, 172] | [156, 285] |
| 11435 | RAF Coastal Command | 2 | [81, 176] | [126, 297] |
| 3238 | Regia Aeronautica | 1 | [136, 255] | [156, 285] |

## 已停用的活跃事件（共 15 条）
- Event `9`: SU Retakes Occupied Areas
- Event `11`: Finland Surrenders
- Event `24`: Italy Surrenders
- Event `78`: Berlin Captured
- Event `93`: Slovakia Surrenders
- Event `94`: Rumania Surrenders
- Event `114`: Soviets Advance into Norway
- Event `123`: Germany Fully Mobilizes
- Event `136`: Soviet Partisan War Ends
- Event `241`: Shortage of Forces in Finland
- Event `242`: Excess Forces in Finland
- Event `245`: Shortage of Forces in Norway
- Event `246`: Excess Forces in Norway
- Event `252`: Soviet Partisans
- Event `277`: Soviet Govt Evacuates Moscow

## 保留单位撤离/战区转移提醒（共 0 条）
- 无待核对的撤离转移。

## 历史豁免与部署覆写 (`force_keep_units`, 共 1 条)
- Unit `2044` (1st): {'X': '0', 'Y': '0', 'ArriveX': '153', 'ArriveY': '290', 'Delay': '1', 'Frozen': '0', 'Morale': '85'} — 1st Fallschirmjaeger-Division (airlifted to Catania Jul 12 1943)

## 非参战部队政策冻结 (`freeze_unit_ids`, 共 11 条)
- Unit `11551` (1st): Frozen 0 -> 12
- Unit `11571` (6th): Frozen 0 -> 12
- Unit `11572` (7th): Frozen 0 -> 12
- Unit `11594` (34th): Frozen 0 -> 12
- Unit `11596` (36th): Frozen 0 -> 12
- Unit `11633` (1st): Frozen 0 -> 12
- Unit `11635` (4th): Frozen 0 -> 12
- Unit `11639` (46th): Frozen 0 -> 12
- Unit `11645` (56th): Frozen 0 -> 12
- Unit `11677` (2nd Tabor Goums): Frozen 0 -> 12
- Unit `11685` (4th Moroccan): Frozen 0 -> 12

## 基于 WITW 史料的士气校准 (`morale_overrides`, 共 12 条)
- Unit `631` (29th): Morale 83 -> 70
- Unit `2044` (1st): Morale 85 -> 85
- Unit `3075` (1/HG Fallschirm Nr.1): Morale 85 -> 70
- Unit `3163` (2/HG Fallschirm Nr.1): Morale 85 -> 70
- Unit `3164` (3/HG Fallschirm Nr.1): Morale 85 -> 70
- Unit `3322` (4th Livorno): Morale 51 -> 40
- Unit `3323` (26th Assietta): Morale 50 -> 40
- Unit `3340` (28th Aosta): Morale 30 -> 35
- Unit `3345` (54th Napoli): Morale 40 -> 35
- Unit `3433` (1/15th): Morale 86 -> 75
- Unit `3434` (2/15th): Morale 86 -> 75
- Unit `3435` (3/15th): Morale 86 -> 75
