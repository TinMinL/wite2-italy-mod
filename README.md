# WitE2 纯意大利战场 Mod (`wite2-italy-mod`)

基于社区大剧本 **[WITW+WITE v0.9.60](https://github.com/Minatoaquadebu/witw-wite-scenario)** 构建的 **Gary Grigsby's War in the East 2 (WitE2 v1.05.02)** 纯意大利战区 Mod 工程、地图逻辑裁剪与校验工具链、大/小剧本蓝图及人类/AI 通用开发避坑指南。

> **为什么需要这个项目？**  
> `WITW+WITE` 把东线、西欧与地中海塞在同一张全欧地图（`378×355 = 134,190` 格）里，单位极多、回合演算耗时。本项目通过 WitE2 原生 `Map NW/SE Limit` 边界裁剪 + CSV 实体/经济清零，实现 **94.1%～98.6% 面积减负**，打造专注于**意大利战场**的大剧本（1943–1945 意大利战役）与小剧本（西西里哈士奇登陆、萨莱诺至罗马）。

---

## 核心特性

1. **大剧本 + 小剧本一体化架构**
   - **大剧本 (`italy_campaign_43_45`)**：1943.7–1945.5 意大利全境战役（`7,920` 格，减负 `94.10%`，`96` 回合）。
   - **小剧本 1 (`italy_husky_43`)**：1943 哈士奇行动·西西里登陆（`1,872` 格，减负 `98.60%`，`8` 回合，直接继承上游实测修正的 `shape2` 滩头与 7 支空降预案）。
   - **小剧本 2 (`italy_avalanche_rome`)**：1943–1944 萨莱诺至罗马/古斯塔夫防线蓝图（`2,500` 格，减负 `98.14%`，`40` 回合）。
2. **安全可复现的 Python CSV 裁剪与校验工具链（不盲改高熵 `.scn` 二进制）**
   - `tools/hex_geometry.py`：严格实现 WitE2 原生 **`shape2`（按行错位）** 六角格邻接、距离与半开区间边界判定。
   - `tools/crop_csv.py`：在保留全部 CSV 槽位行号不变的前提下，安全置空框外单位、清零框外城市工业/补给、清理 `thBoxLock`、并自动将框外祖先高司 HQ 迁入配置锚点。
   - `tools/validate_csv.py`：6 项离线硬核校验（Schema、边界、HQ 链、堆叠上限、航空基地、Husky `shape2` 几何）。
   - `tools/analyze_upstream_italy.py`：从上游 `WITW+WITE v0.9.60` 数据提炼纯意大利基线 JSON 与审计表。
3. **写给人也写给所有 AI 看的开发避坑手册**
   - 详见 [AI_DEV_GUIDE.md](AI_DEV_GUIDE.md)：记录 14 条实测与继承避坑经验（`shape2` vs `shape3`、`SE-1` 边界、Campaign 模式柏林陷落硬编码、空降规模上限 9、国家 12 套皮副作用、CSV 槽位铁律等）。

---

## 文档与目录导航

- **[AI_DEV_GUIDE.md](AI_DEV_GUIDE.md)**：人类与 AI 开发者必读的架构铁律、引擎坑点与 Quickstart。
- **[docs/SCENARIO_BLUEPRINT.md](docs/SCENARIO_BLUEPRINT.md)**：三大剧本的坐标盒、VP、人力与船池设计蓝图。
- **[docs/EDITOR_WORKFLOW.md](docs/EDITOR_WORKFLOW.md)**：WitE2 编辑器 `Export CSV → Python 裁剪 → Import CSV → 收尾校验` 完整步骤。
- **[docs/ITALY_BASELINE_AUDIT.md](docs/ITALY_BASELINE_AUDIT.md)**：从上游 `v0.9.60` 自动提炼的意大利城市 VP 与哈士奇登陆/空降审计表。
- **[CHANGELOG.md](CHANGELOG.md)**：更新日志与验证边界说明。

---

## 快速验证与运行

在项目根目录（`意大利mod/`）运行：

```powershell
# 1. 运行自动化回归测试（shape2 几何 + 官方 Velikie Luki 真实 CSV 端到端裁剪校验 + 基线完整性）
python -m unittest discover -s tests -v

# 2. 对 WitE2 Editor 导出的全套 CSV 执行预览裁剪（以西西里小剧本为例）
python tools/crop_csv.py --input-dir "..\Dat\CSV" --prefix "WITW+WITE v0.9.60" --config "config\italy_husky_43.json" --output-dir "output\husky_csv" --dry-run --relocate-offmap-hqs --report "output\husky_crop_report.md"
```

---

## 当前验证状态（诚实边界）

- **已通过自动化验证**：
  - `shape2` 六角格几何已对照上游 `husky-coastline-fix.json` 的实机逆向邻接表逐一回归通过。
  - `crop_csv.py` 与 `validate_csv.py` 已在游戏官方 `Dat/CSV/Introductory Scenario 1 - Velikie Luki_*.csv`（16,384 单位行 / 4,096 航空队行）上跑通端到端裁剪与零报错校验。
- **待实机操作验证**：
  - 本仓库不包含 `WarInTheEast2.exe` 或上游二进制 `.scn`/`.tga` 文件。需玩家/作者按 [docs/EDITOR_WORKFLOW.md](docs/EDITOR_WORKFLOW.md) 在本地 WitE2 编辑器导出 `WITW+WITE v0.9.60.scn` 的 CSV 后回灌保存，并在游戏内验证 T1 后勤、登陆与 AI 表现。

---

## 来源、署名与版权声明

- 原始社区融合剧本 **WITW+WITE v0.9** 作者：**yyuegu**（[Matrix Games 原帖](https://forums.matrixgames.com/viewtopic.php?t=407304)）。
- 上游修复版 **WITW+WITE v0.9.60** 维护者：**[Minatoaquadebu/witw-wite-scenario](https://github.com/Minatoaquadebu/witw-wite-scenario)**。
- 本仓库仅包含原创裁剪配置、Python 工具链、测试与开发文档，**不包含** Matrix Games / 2by3 Games 原版游戏程序、全局 `.dat` 数据库或上游 `.scn`/`.tga` 二进制文件。游戏本体及原始数据权利归各自权利方所有。
