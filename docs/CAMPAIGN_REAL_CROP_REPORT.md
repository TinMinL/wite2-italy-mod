# CSV 裁剪审计报告 — `italy_campaign_43_45`

- **CSV 格式**：`new`
- **来源标识**：`WITW+WITE v0.9.65`
- **Dry Run**：`False`
- **有效坐标盒**：`NW=[57, 202]`, `SE=[176, 318]`（排除区 `2` 个）

## 实体裁剪统计
- **保留单位**：`810`（含机场 `205`）
- **停用/置空框外单位**：`9676`
- **保留航空队**：`337`
- **停用/置空框外航空队**：`1842`
- **框内城市**：`435`（其中港口 `60` 座）
- **已清零经济/补给的框外城市**：`3628`
- **清理残留 TB / Lock 字段**：`58`
- **活跃事件保留 / 停用**：`176` / `13`

## 需迁移或已自动迁移的祖先 HQ（共 11 个）
| Unit ID | 名称 | Player | 原坐标 | 建议锚点坐标 |
| --- | --- | --- | --- | --- |
| 2 | OKL | 1 | [135, 180] | [131, 235] |
| 2000 | OKW | 1 | [139, 172] | [131, 235] |
| 2833 | OB West | 1 | [90, 198] | [131, 235] |
| 1 | OKH | 1 | [139, 174] | [131, 235] |
| 11421 | RAF HQ | 2 | [82, 176] | [126, 297] |
| 11422 | USSTAF | 2 | [80, 176] | [126, 297] |
| 11418 | SHAEF | 2 | [80, 176] | [126, 297] |
| 3276 | XXII | 1 | [105, 244] | [131, 235] |
| 2887 | LXXXVI | 1 | [70, 236] | [131, 235] |
| 2842 | 1st | 1 | [73, 229] | [131, 235] |
| 11435 | RAF Coastal Command | 2 | [81, 176] | [126, 297] |

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

## 历史豁免与部署覆写 (`force_keep_units`, 共 36 条)
- Unit `2014` (XI Fallschirm Flieger): {'X': '0', 'Y': '0', 'ArriveX': '142', 'ArriveY': '257', 'Delay': '1', 'Frozen': '0', 'HigherHQ': '3240', 'TheaterBox': '0'} — XI Fallschirm Flieger Corps (T2 Rome SE)
- Unit `2861` (LXXVI): {'X': '0', 'Y': '0', 'ArriveX': '113', 'ArriveY': '230', 'Delay': '3', 'Frozen': '0', 'HigherHQ': '3240', 'TheaterBox': '0'} — LXXVI Panzer Corps (from France -> Turin)
- Unit `3243` (10th): {'X': '0', 'Y': '0', 'ArriveX': '139', 'ArriveY': '208', 'Delay': '6', 'Frozen': '0', 'HigherHQ': '3240', 'TheaterBox': '0'} — 10th Army HQ (from TB=7 -> Bolzano/N.Italy)
- Unit `3244` (14th): {'X': '0', 'Y': '0', 'ArriveX': '136', 'ArriveY': '206', 'Delay': '20', 'Frozen': '0', 'HigherHQ': '3240', 'TheaterBox': '0'} — 14th Army HQ (N.Italy)
- Unit `3259` (LXXV): {'X': '0', 'Y': '0', 'ArriveX': '144', 'ArriveY': '204', 'Delay': '28', 'Frozen': '0', 'HigherHQ': '3240', 'TheaterBox': '0'} — LXXV Corps HQ (N.Italy)
- Unit `2044` (1st): {'X': '0', 'Y': '0', 'ArriveX': '142', 'ArriveY': '257', 'Delay': '1', 'Frozen': '0', 'Morale': '85', 'HigherHQ': '3240', 'TheaterBox': '0'} — 1st Fallschirmjaeger-Division (from S.France -> Rome SE)
- Unit `2907` (26th): {'X': '0', 'Y': '0', 'ArriveX': '128', 'ArriveY': '230', 'Delay': '4', 'Frozen': '0', 'Morale': '80', 'HigherHQ': '3240', 'TheaterBox': '0'} — 26th Panzer Division (from France -> N.Italy)
- Unit `2919` (2nd): {'X': '0', 'Y': '0', 'ArriveX': '136', 'ArriveY': '254', 'Delay': '4', 'Frozen': '0', 'Morale': '85', 'HigherHQ': '3240', 'TheaterBox': '0'} — 2nd Fallschirmjaeger-Division (from TB=7 -> Rome)
- Unit `2941` (65th): {'X': '0', 'Y': '0', 'ArriveX': '128', 'ArriveY': '230', 'Delay': '5', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 65th Infantry Division (from France -> N.Italy)
- Unit `3001` (305th): {'X': '0', 'Y': '0', 'ArriveX': '139', 'ArriveY': '208', 'Delay': '11', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 305th Infantry Division (from France -> Alps)
- Unit `3042` (356th): {'X': '0', 'Y': '0', 'ArriveX': '145', 'ArriveY': '206', 'Delay': '17', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 356th Infantry Division (from TB=7 -> Alps)
- Unit `693` (44th): {'X': '0', 'Y': '0', 'ArriveX': '139', 'ArriveY': '208', 'Delay': '18', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 44th HuD Infantry Division (from Austria -> Alps)
- Unit `3856` (5th): {'X': '0', 'Y': '0', 'ArriveX': '139', 'ArriveY': '208', 'Delay': '24', 'Frozen': '0', 'Morale': '80', 'HigherHQ': '3240', 'TheaterBox': '0'} — 5th Mountain Division (from East -> Alps)
- Unit `715` (71st): {'X': '0', 'Y': '0', 'ArriveX': '139', 'ArriveY': '208', 'Delay': '25', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 71st Infantry Division (from Germany -> Alps)
- Unit `2079` (334th): {'X': '0', 'Y': '0', 'ArriveX': '126', 'ArriveY': '232', 'Delay': '27', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 334th Infantry Division (from S.France -> N.Italy)
- Unit `3302` (4th): {'X': '0', 'Y': '0', 'ArriveX': '136', 'ArriveY': '227', 'Delay': '27', 'Frozen': '0', 'Morale': '80', 'HigherHQ': '3240', 'TheaterBox': '0'} — 4th Fallschirmjaeger-Division (historical Del=27 Venice)
- Unit `3053` (715th): {'X': '0', 'Y': '0', 'ArriveX': '112', 'ArriveY': '235', 'Delay': '29', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 715th Infantry Division (from TB=7 -> Liguria)
- Unit `3386` (1027th): {'X': '0', 'Y': '0', 'ArriveX': '128', 'ArriveY': '204', 'Delay': '29', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 1027th Mot Grenadier Brigade (from TB=7 -> Alps)
- Unit `3390` (1028th): {'X': '0', 'Y': '0', 'ArriveX': '144', 'ArriveY': '204', 'Delay': '29', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 1028th Grenadier Regiment (from TB=7 -> Alps)
- Unit `3882` (114th): {'X': '0', 'Y': '0', 'ArriveX': '145', 'ArriveY': '206', 'Delay': '32', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 114th Jaeger Division (from TB=7 -> Alps)
- Unit `2063` (92nd): {'X': '0', 'Y': '0', 'ArriveX': '129', 'ArriveY': '227', 'Delay': '41', 'Frozen': '0', 'Morale': '65', 'HigherHQ': '3240', 'TheaterBox': '0'} — 92nd Infantry Division (N.Italy)
- Unit `2181` (20th Sturm): {'X': '0', 'Y': '0', 'ArriveX': '145', 'ArriveY': '206', 'Delay': '49', 'Frozen': '0', 'Morale': '60', 'HigherHQ': '3240', 'TheaterBox': '0'} — 20th Luftwaffe Field Division (from TB=4 -> Alps)
- Unit `2954` (98th): {'X': '0', 'Y': '0', 'ArriveX': '139', 'ArriveY': '208', 'Delay': '58', 'Frozen': '0', 'Morale': '65', 'HigherHQ': '3240', 'TheaterBox': '0'} — 98th Infantry Division (Alps)
- Unit `3868` (42nd): {'X': '0', 'Y': '0', 'ArriveX': '123', 'ArriveY': '231', 'Delay': '61', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 42nd Jaeger Division (from TB=7 -> Po Valley)
- Unit `3328` (232nd): {'X': '0', 'Y': '0', 'ArriveX': '125', 'ArriveY': '227', 'Delay': '69', 'Frozen': '0', 'Morale': '60', 'HigherHQ': '3240', 'TheaterBox': '0'} — 232nd Infantry Division (N.Italy)
- Unit `3532` (710th): {'X': '0', 'Y': '0', 'ArriveX': '139', 'ArriveY': '208', 'Delay': '79', 'Frozen': '0', 'Morale': '55', 'HigherHQ': '3240', 'TheaterBox': '0'} — 710th Infantry Division (from TB=4 -> Alps)
- Unit `2328` (242nd): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '0', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 242nd StuG Battalion (SU attached to Army Group C)
- Unit `3394` ('Meyer'): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '6', 'Frozen': '0', 'Morale': '80', 'HigherHQ': '3240', 'TheaterBox': '0'} — 'Meyer' Heavy Panzer Company (SU -> Army Group C)
- Unit `1097` (525th): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '8', 'Frozen': '0', 'Morale': '80', 'HigherHQ': '3240', 'TheaterBox': '0'} — 525th Nashorn Heavy PzJg Bn (SU -> Army Group C)
- Unit `2369` (93rd): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '10', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 93rd Nashorn Heavy PzJg Bn (SU -> Army Group C)
- Unit `3398` (590th): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '17', 'Frozen': '0', 'Morale': '70', 'HigherHQ': '3240', 'TheaterBox': '0'} — 590th Heavy PzJg Bn (SU -> Army Group C)
- Unit `2344` (907th): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '28', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 907th StuG Battalion (SU -> Army Group C)
- Unit `2348` (914th): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '28', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 914th StuG Battalion (SU -> Army Group C)
- Unit `3084` (508th): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '31', 'Frozen': '0', 'Morale': '85', 'HigherHQ': '3240', 'TheaterBox': '0'} — 508th Tiger Heavy Panzer Bn (SU -> Army Group C)
- Unit `1070` (653rd): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '31', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 653rd Ferdinand Heavy PzJg Bn (SU -> Army Group C)
- Unit `2353` (11th Fallschirm): {'X': '0', 'Y': '0', 'ArriveX': '0', 'ArriveY': '0', 'Delay': '36', 'Frozen': '0', 'Morale': '75', 'HigherHQ': '3240', 'TheaterBox': '0'} — 11th Fallschirm StuG Bn (SU -> Army Group C)

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
