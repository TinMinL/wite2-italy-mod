# WitE2 纯意大利战场 Mod (`wite2-italy-mod`)

基于社区大剧本 **[WITW+WITE v0.9.60](https://github.com/Minatoaquadebu/witw-wite-scenario)** 构建的 **Gary Grigsby's War in the East 2 (WitE2 v1.05.02)** 纯意大利战区 Mod 工程、New Editor 20 文件 CSV 逻辑裁剪与校验工具链、大/小剧本蓝图及人类/AI 通用开发避坑指南。

> **为什么需要这个项目？**  
> `WITW+WITE` 把东线、西欧与地中海塞在同一张全欧地图（`378×355 = 134,190` 格）里，单位极多、回合演算耗时。本项目通过 WitE2 原生 `Map NW/SE Limit` 边界裁剪 + 矩形排除区 (`exclude_boxes`) + New Editor CSV 实体/机场/事件/经济裁剪，实现 **90.25%～96.83% 面积减负**与 **93%～96% 单位裁剪**，打造专注于**意大利战场**的大剧本（1943–1945 意大利战役）与小剧本（西西里哈士奇登陆、萨莱诺至罗马）。

---

## 核心特性

1. **大剧本 + 小剧本一体化架构（已基于真实 `v0.9.60` CSV 跑通裁剪与零报错校验）**
   - **大剧本 (`italy_campaign_43_45`)**：1943.7–1945.5 意大利全境战役（`NW=[57,208], SE=[176,318]` 结合南法/巴尔干排除区，削减 `90.25%` 面积；真实裁剪保留 `729` 单位 / `173` 机场 / `241` 航空队，停用 `9,733` 无关单位）。
   - **小剧本 1 (`italy_husky_43`)**：1943 哈士奇行动·西西里登陆（`NW=[57,275], SE=[166,314]` 结合撒丁排除区，削减 `96.83%` 面积；真实裁剪保留 `424` 单位 / `55` 机场 / `159` 航空队，完整保留全部 6 支两栖 TF 与 7 支空降预案）。
   - **小剧本 2 (`italy_avalanche_rome`)**：1943–1944 萨莱诺至罗马/古斯塔夫防线蓝图（`2,500` 格，削减 `98.14%` 面积）。
2. **安全可复现的 Python CSV 裁剪与校验工具链（兼容 New Editor & Old Editor）**
   - `tools/hex_geometry.py`：严格实现 WitE2 原生 **`shape2`（按行错位）** 六角格邻接/距离、`SE-1` 半开区间与 `exclude_boxes` 排除区判定。
   - `tools/crop_csv.py`：
     - 支持 **v1.05.02 New Editor 20 文件子目录格式**与旧版前缀格式；
     - 通过 `Locations.AbUnit` 精准保留框内机场（解决 `Units.csv` 中机场坐标为 `0,0` 的坑）；
     - 不删行保槽位、原样保留 `ISO-8859-1` (`Pilots.csv`) 编码、按列表流式裁剪 `GameEvents.csv` 变长尾列；
     - 自动将框外祖先高司 HQ 迁入配置锚点（`--relocate-offmap-hqs`）。
   - `tools/validate_csv.py`：7 项离线硬核校验（Schema、边界/排除区、HQ 链、堆叠上限、机场 `AbUnit` 链接、事件策略、Husky `shape2` 几何）。
   - 可与社区工具 **[mlshort/wite2_tools](https://github.com/mlshort/wite2_tools)** 联用，在导入前做 `audit-batch` / `gen-orphans` 深度数据库体检。
3. **写给人也写给所有 AI 看的开发避坑手册**
   - 详见 [AI_DEV_GUIDE.md](AI_DEV_GUIDE.md)：记录 19 条实测与继承避坑经验。

---

## 文档与目录导航

- **[AI_DEV_GUIDE.md](AI_DEV_GUIDE.md)**：人类与 AI 开发者必读的架构铁律、引擎坑点（含 New Editor 20 文件与 `wite2_tools` 协作）与 Quickstart。
- **[docs/EDITOR_WORKFLOW.md](docs/EDITOR_WORKFLOW.md)**：WitE2 New Editor（紫色 `CSV` 标签页）`Export → 裁剪 → Import → 收尾校验` 完整步骤。
- **[docs/SCENARIO_BLUEPRINT.md](docs/SCENARIO_BLUEPRINT.md)**：三大剧本的坐标盒、排除区、真实裁剪统计与 VP/人力设计蓝图。
- **[docs/HUSKY_REAL_CROP_REPORT.md](docs/HUSKY_REAL_CROP_REPORT.md)** & **[docs/CAMPAIGN_REAL_CROP_REPORT.md](docs/CAMPAIGN_REAL_CROP_REPORT.md)**：基于真实 `WITW+WITE v0.9.60` CSV 跑出的详细裁剪审计报告。
- **[docs/ITALY_BASELINE_AUDIT.md](docs/ITALY_BASELINE_AUDIT.md)**：上游基线提炼审计表。
- **[CHANGELOG.md](CHANGELOG.md)**：更新日志与验证边界说明。

---

## 快速验证与运行

在项目根目录（`意大利mod/`）运行：

```powershell
# 1. 运行自动化回归测试（8 项全覆盖：shape2 几何 + Old/New Editor 真实 CSV 端到端裁剪校验 + 编码/变长尾列保真）
python -m unittest discover -s tests -v

# 2. 对 New Editor 导出的 WITW+WITE v0.9.60 目录执行裁剪（以西西里小剧本为例）
python tools/crop_csv.py --input-dir "..\Dat\CSV\WITW+WITE v0.9.60" --config "config\italy_husky_43.json" --output-dir "output\Italy_Husky_43" --relocate-offmap-hqs --report "docs\HUSKY_REAL_CROP_REPORT.md"
python tools/validate_csv.py --input-dir "output\Italy_Husky_43" --config "config\italy_husky_43.json"
```

---

## 当前验证状态（诚实边界）

- **已通过自动化与真实数据静态验证**：
  - `shape2` 六角格几何已对照上游 `husky-coastline-fix.json` 实机逆向邻接表逐一回归通过。
  - `crop_csv.py` 与 `validate_csv.py` 已在本地真实导出的 `Dat\CSV\WITW+WITE v0.9.60\`（13,045 单位行 / 2,643 航空队行 / 4,431 地点行 / 452 事件行）上跑通 `Italy_Husky_43` 与 `Italy_Campaign_43_45` 全量裁剪与零报错校验（`errors == []`），且 `Pilots.csv` SHA256 与 `GameEvents.csv` 变长列结构 100% 保持。
- **待实机操作验证**：
  - 需在本地 WitE2 New Editor 中对 `output\Italy_Husky_43\` 和 `output\Italy_Campaign_43_45\` 执行 `Import from CSV`、设置 `Main Tab` 边界并运行 `DAMAGE OFF-MAP RAIL` 后另存 `.scn`，进游戏实机跑通 T1~T2。

---

## 来源、署名与版权声明

- 原始社区融合剧本 **WITW+WITE v0.9** 作者：**yyuegu**（[Matrix Games 原帖](https://forums.matrixgames.com/viewtopic.php?t=407304)）。
- 上游修复版 **WITW+WITE v0.9.60** 维护者：**[Minatoaquadebu/witw-wite-scenario](https://github.com/Minatoaquadebu/witw-wite-scenario)**。
- 本仓库仅包含原创裁剪配置、Python 工具链、测试、审计报告与开发文档，**不包含** Matrix Games / 2by3 Games 原版游戏程序、全局 `.dat` 数据库或上游 `.scn`/`.tga` 二进制文件。游戏本体及原始数据权利归各自权利方所有。
