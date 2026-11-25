# CSV 裁剪审计报告 — `italy_campaign_43_45`

- **CSV 格式**：`new`
- **来源标识**：`WITW+WITE v0.9.60`
- **Dry Run**：`False`
- **有效坐标盒**：`NW=[57, 208]`, `SE=[176, 318]`（排除区 `2` 个）

## 实体裁剪统计
- **保留单位**：`732`（含机场 `173`）
- **停用/置空框外单位**：`9730`
- **保留航空队**：`241`
- **停用/置空框外航空队**：`1918`
- **框内城市**：`391`（其中港口 `60` 座）
- **已清零经济/补给的框外城市**：`3671`
- **清理残留 TB / Lock 字段**：`59`
- **活跃事件保留 / 停用**：`176` / `13`

## 需迁移或已自动迁移的祖先 HQ（共 12 个）
| Unit ID | 名称 | Player | 原坐标 | 建议锚点坐标 |
| --- | --- | --- | --- | --- |
| 2 | OKL | 1 | [135, 180] | [131, 235] |
| 2000 | OKW | 1 | [139, 172] | [131, 235] |
| 11421 | RAF HQ | 2 | [82, 176] | [126, 297] |
| 2887 | LXXXVI | 1 | [70, 236] | [131, 235] |
| 2842 | 1st | 1 | [73, 229] | [131, 235] |
| 2833 | OB West | 1 | [90, 198] | [131, 235] |
| 11422 | USSTAF | 2 | [80, 176] | [126, 297] |
| 1 | OKH | 1 | [139, 174] | [131, 235] |
| 11418 | SHAEF | 2 | [80, 176] | [126, 297] |
| 11435 | RAF Coastal Command | 2 | [81, 176] | [126, 297] |
| 2836 | Army Group H | 1 | [116, 173] | [131, 235] |
| 3276 | XXII | 1 | [105, 244] | [131, 235] |

## 已停用的活跃事件（共 13 条）
- Event `9`: SU Retakes Occupied Areas
- Event `11`: Finland Surrenders
- Event `78`: Berlin Captured
- Event `93`: Slovakia Surrenders
- Event `94`: Rumania Surrenders
- Event `114`: Soviets Advance into Norway
- Event `136`: Soviet Partisan War Ends
- Event `241`: Shortage of Forces in Finland
- Event `242`: Excess Forces in Finland
- Event `245`: Shortage of Forces in Norway
- Event `246`: Excess Forces in Norway
- Event `252`: Soviet Partisans
- Event `277`: Soviet Govt Evacuates Moscow

## 保留单位撤离/战区转移提醒（共 0 条）
- 无待核对的撤离转移。

## 历史豁免与部署覆写 (`force_keep_units`, 共 2 条)
- Unit `2044` (1st): {'X': '0', 'Y': '0', 'ArriveX': '142', 'ArriveY': '257', 'Delay': '1', 'Frozen': '0', 'Morale': '85'} — 1st Fallschirmjaeger-Division (exempt from Southern France exclude box, deploys to Italy T2 per WITW)
- Unit `2014` (XI Fallschirm Flieger): {'X': '0', 'Y': '0', 'ArriveX': '142', 'ArriveY': '257', 'Delay': '1', 'Frozen': '0'} — XI Fallschirm Flieger Corps (exempt from Southern France exclude box, deploys to Rome SE T2)

## 非参战部队政策冻结 (`freeze_unit_ids`, 共 0 条)
- 无。

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
