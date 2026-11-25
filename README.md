# WitE2 纯意大利战场 Mod (`wite2-italy-mod`)

基于社区大剧本 **[WITW+WITE v0.9.65](https://github.com/Minatoaquadebu/witw-wite-scenario)** 构建的 **Gary Grigsby's War in the East 2 (WitE2 v1.05.02)** 纯意大利战区 Mod 工程、New Editor 20 文件 CSV 逻辑裁剪与校验工具链、大/小剧本蓝图及人类/AI 通用开发避坑指南。

> **为什么需要这个项目？**  
> `WITW+WITE` 把东线、西欧与地中海塞在同一张全欧地图（`378×355 = 134,190` 格）里，单位极多、回合演算耗时。本项目通过 WitE2 原生 `Map NW/SE Limit` 边界裁剪 + 矩形排除区 (`exclude_boxes`) + New Editor CSV 实体/机场/事件/经济裁剪，实现 **89.71%～96.43% 面积减负**与 **90%～96% 单位裁剪**，打造专注于**意大利战场**的大剧本（1943–1945 意大利战役）与小剧本（西西里哈士奇登陆、萨莱诺至罗马）。

---

## 快速下载与安装（即下即玩）

如果你想直接下载目前已发布的双剧本可玩包（**`v0.4.0`**：含 **西西里 8 回合小剧本 `Italy_Husky_43`** 与 **1943–1945 意大利全战役 96 回合大剧本 `Italy_Campaign_43_45`**，均基于 `WITW+WITE v0.9.65` + 官方 WITW 史料校准）：
1. 前往本仓库 **[Releases (`v0.4.0`)](https://github.com/TinMinL/wite2-italy-mod/releases/tag/v0.4.0)** 下载 `wite2-italy-mod-v0.4.0.zip` 并解压（也可直接从仓库 `Dat/Scen/` 与 `Dat/Scen_ZH/` 获取对应 `.scn` 与 `.txt`）。
2. 将解压后的 `Dat/Scen/*.scn` 与默认英文纯 ASCII 简介 `Dat/Scen/*.txt` **一起复制**到你的 **War in the East 2 安装目录下的 `Dat\Scen\` 文件夹**。
3. **中文玩家可选步骤**：若你的游戏已安装中文字库汉化包（如 `WITE2_CN_10502`），可再将 `Dat/Scen_ZH/*.txt`（UTF-8 with BOM 编码）覆盖复制到游戏 `Dat\Scen\`，即可在选剧本界面显示中文背景与 T1 操作提示。
4. 启动游戏（推荐双方先设 **Human** 测试），点 **`Pick Scenario`** 选择 **`Italy_Husky_43`** 或 **`Italy_Campaign_43_45`** 即可直接开局。

---

## 核心特性

1. **大剧本 + 小剧本一体化架构（已基于真实 `v0.9.65` CSV + 官方 WITW 史料校准跑通零报错校验）**
   - **大剧本 (`italy_campaign_43_45`)**：1943.7–1945.5 意大利全境战役（`NW=[57,202], SE=[176,318]` 结合南法/巴尔干排除区，削减 `89.71%` 面积；真实裁剪保留 `810` 单位 / `205` 机场 / `337` 航空队，依据官方 WITW `Battleground Italy 43-45` 恢复全部 **36 支**法国/奥地利/预备队德军师、第 10/14 集团军及 508 虎式/653 象式等精锐支援营）。
   - **小剧本 1 (`italy_husky_43`)**：1943 哈士奇行动·西西里登陆（`NW=[57,270], SE=[166,314]` 结合撒丁排除区，削减 `96.43%` 面积；真实裁剪保留 `435` 单位 / `61` 机场 / `185` 航空队，完整保留第 29 装掷师、第 1 伞兵师、6 支两栖 TF 与 7 支空降预案，冻结 11 支萨莱诺师并按官方 WITW 校准德意士气）。
   - **小剧本 2 (`italy_avalanche_rome`)**：1943–1944 萨莱诺至罗马/古斯塔夫防线蓝图（`2,500` 格，削减 `98.14%` 面积）。
2. **安全可复现的 Python CSV 裁剪与校验工具链（兼容 New Editor & Old Editor + 上游 `v0.9.65`）**
   - `tools/hex_geometry.py`：严格实现 WitE2 原生 **`shape2`（按行错位）** 六角格邻接/距离、`SE-1` 半开区间与 `exclude_boxes` 排除区判定。
   - `tools/crop_csv.py`：
     - 支持 **v1.05.02 New Editor 20 文件子目录格式**与旧版前缀格式；
     - 支持 `force_keep_units` 历史豁免（含 `higher_hq`/`theater_box` 覆写）、`freeze_unit_ids` 政策冻结、`morale_overrides` 士气校准；
     - 通过 `Locations.AbUnit` 精准保留框内机场，并自动将框外在图/延迟祖先 HQ 迁入配置锚点；
     - 不删行保槽位、原样保留 `ISO-8859-1` (`Pilots.csv`) 编码、按列表流式裁剪 `GameEvents.csv` 变长尾列。
   - `tools/compare_witw_husky.py`：直接对比官方 WITW *Operation Husky* CSV 与本项目输出，自动生成 [docs/WITW_HUSKY_COMPARISON.md](docs/WITW_HUSKY_COMPARISON.md)。
   - `tools/validate_csv.py`：7 项离线硬核校验（Schema、边界/排除区、HQ 链、堆叠上限、机场 `AbUnit` 链接、事件策略、Husky `shape2` 几何）。
   - 可与社区工具 **[mlshort/wite2_tools](https://github.com/mlshort/wite2_tools)** 联用，在导入前做 `audit-batch` / `gen-orphans` 深度数据库体检。
3. **写给人也写给所有 AI 看的开发避坑手册**
   - 详见 [AI_DEV_GUIDE.md](AI_DEV_GUIDE.md)：记录 21 条实测与继承避坑经验（含 `v0.9.65` 升级流程与大剧本德军增援清单）。

---

## 文档与目录导航

- **[AI_DEV_GUIDE.md](AI_DEV_GUIDE.md)**：人类与 AI 开发者必读的架构铁律、引擎坑点与 Quickstart。
- **[docs/WITW_HUSKY_COMPARISON.md](docs/WITW_HUSKY_COMPARISON.md)**：官方 WITW《哈士奇行动》vs 本项目实测对照表。
- **[docs/EDITOR_WORKFLOW.md](docs/EDITOR_WORKFLOW.md)**：WitE2 New Editor（紫色 `CSV` 标签页）`Export → 裁剪 → Import → 收尾校验` 完整步骤。
- **[docs/SCENARIO_BLUEPRINT.md](docs/SCENARIO_BLUEPRINT.md)**：三大剧本的坐标盒、排除区、真实裁剪统计与 VP/人力设计蓝图。
- **[docs/HUSKY_REAL_CROP_REPORT.md](docs/HUSKY_REAL_CROP_REPORT.md)** & **[docs/CAMPAIGN_REAL_CROP_REPORT.md](docs/CAMPAIGN_REAL_CROP_REPORT.md)**：详细裁剪审计报告。
- **[docs/ITALY_BASELINE_AUDIT.md](docs/ITALY_BASELINE_AUDIT.md)**：上游基线提炼审计表。
- **[CHANGELOG.md](CHANGELOG.md)**：更新日志与验证边界说明。

---

## 快速验证与运行

在项目根目录（`意大利mod/`）运行：

```powershell
# 1. 运行自动化回归测试（8 项全覆盖：shape2 几何 + Old/New Editor 真实 CSV 端到端裁剪校验 + 编码/变长尾列保真）
python -m unittest discover -s tests -v

# 2. 对 New Editor 导出的 WITW+WITE v0.9.65 目录执行裁剪（以西西里小剧本为例）
python tools/crop_csv.py --input-dir "..\Dat\CSV\WITW+WITE v0.9.65" --config "config\italy_husky_43.json" --output-dir "output\Italy_Husky_43" --relocate-offmap-hqs --report "docs\HUSKY_REAL_CROP_REPORT.md"
python tools/validate_csv.py --input-dir "output\Italy_Husky_43" --config "config\italy_husky_43.json"
```

---

## 当前验证状态（诚实边界）

- **已通过实机编辑器导入与 `v0.9.65` 静态校验**：
  - `shape2` 六角格几何、`crop_csv.py` 与 `validate_csv.py` 已在真实 `Dat\CSV\WITW+WITE v0.9.65\` 上通过 8/8 自动化回归测试（`Italy_Husky_43` 与 `Italy_Campaign_43_45` 均 `errors == []`）。
  - `v0.4.0` 的两份可玩剧本 [Dat/Scen/Italy_Husky_43.scn](Dat/Scen/Italy_Husky_43.scn)（`2.20 MB`）与 [Dat/Scen/Italy_Campaign_43_45.scn](Dat/Scen/Italy_Campaign_43_45.scn)（`2.21 MB`）均已在 **WitE2 v1.05.02 New Editor** 完成 20 文件 CSV 批量 `Import from CSV`（均报 **`Batch import: Errors: 0, Warnings: 4`**，4 条为上游 `OBs.csv` 原有空槽提示）、Main Tab 边界/胜利条件设置与铁路/港口初始化并保存；且已补充英文纯 ASCII (`Dat/Scen/*.txt`) 与中文 UTF-8 BOM (`Dat/Scen_ZH/*.txt`) 双语简介。
- **待实机游玩验证**：
  - `v0.4.0` 的两份 `.scn` 待进入正式游戏实测 T1~T2 两栖 `INVADE`、空降落地、大剧本德军增援按回合到达与过回合耗时表现。

---

## 来源、署名与版权声明

- 原始社区融合剧本 **WITW+WITE v0.9** 作者：**yyuegu**（[Matrix Games 原帖](https://forums.matrixgames.com/viewtopic.php?t=407304)）。
- 上游修复版 **WITW+WITE v0.9.60–v0.9.65** 维护者：**[Minatoaquadebu/witw-wite-scenario](https://github.com/Minatoaquadebu/witw-wite-scenario)**。
- 本仓库包含原创裁剪配置、Python 工具链、测试、审计报告、开发文档以及经裁剪衍生的社区剧本文件 `Dat/Scen/Italy_Husky_43.scn` 与 `Dat/Scen/Italy_Campaign_43_45.scn`（不含游戏本体 EXE 或原版全局 `.dat` 数据库）。未将原社区作品或游戏数据重新授权为 MIT 等开源许可，游戏本体及原始数据权利归各自权利方所有。
