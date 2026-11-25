# 更新日志 (`CHANGELOG.md`)

所有重要变更、工具链验证范围与待实机核对项均记录在此。

---

## [v0.4.0-dev] - 2026-11-25（官方 WITW 史料大修 + 上游 `v0.9.65` 母版预置）

### 重大改进
- **预置上游最新母版 `WITW+WITE v0.9.65`**：下载并通过 SHA256 校验（`a437b391...`）解压至只读基线 `source/witw-wite-v0.9.65/`，已将 `WITW+WITE v0.9.65.scn` 与 `.txt` 部署至游戏 `Dat\Scen\` 待导出。上游 `v0.9.61–v0.9.65` 补齐了威尼斯德军铁路司令部、41 座仓库、235 支战区轴心航空队、2,338 名轴心飞行员、5,793 架备用机及 20 万卡车/2,000 飞行员池。
- **裁剪引擎新增声明式历史校准能力 (`tools/crop_csv.py`)**：
  - 新增 `force_keep_units`（历史参战豁免与部署覆写）、`freeze_unit_ids`（非参战师冻结）与 `morale_overrides`（士气校准）；
  - 修复延迟增援祖先 HQ（如 `2836 Army Group H` 在 `(116,173)`）在向上闭包时未重定位 `ArriveX/ArriveY` 的缺陷。
- **依据本地官方 WITW《哈士奇行动》CSV 完成历史大修**：
  - `italy_husky_43.json` 北界从 `Y=275` 移至 `Y=270`，找回卡拉布里亚 **第 29 装甲掷弹兵师 (`631`)**；豁免保留 **第 1 伞兵师 (`2044`)** 于 T2 空运至卡塔尼亚 `(153,290)`；冻结 11 支 9 月萨莱诺/半岛盟军师（`Frozen=12`），使开局未冻结参战盟军保持在 19 支（对齐官方 WITW 18 支 + `509th`）；德意核心师士气对标 WITW 回调（`HG 70`, `15th PzGr 75`, `29th PzGr 70`, `1st FJ 85`, 意四师 `40/40/35/35`）。
  - `italy_campaign_43_45.json` 同步豁免保留第 1 伞兵师 (`2044`) 与 XI 伞兵军 (`2014`) 于 T2 部署罗马东南 `(142,257)`，并同步上述士气校准。
- **新增 WITW 对照脚本与报告**：[tools/compare_witw_husky.py](tools/compare_witw_husky.py) 与 [docs/WITW_HUSKY_COMPARISON.md](docs/WITW_HUSKY_COMPARISON.md)。

### 已完成验证（自动化与真实 CSV）
- `python -m unittest discover -s tests -v`：8/8 测试全部通过（已包含第 29 师/第 1 伞兵师/士气校准/11 师冻结/Campaign 豁免断言）。
- 基于当前已导出 `WITW+WITE v0.9.60` CSV 重跑 `Italy_Husky_43`（433 单位 / 60 机场 / 159 航空队）与 `Italy_Campaign_43_45`（732 单位 / 173 机场 / 241 航空队）：均返回 **`errors: []`、`overstack_hexes: 0`、`husky_geometry_errors: 0`**。

### 下一步待办（`v0.4.0` 实机发布）
- 在 WitE2 New Editor 打开 `WITW+WITE v0.9.65.scn` 点一次 `Export to CSV`，随后用 `crop_csv.py` 重跑大/小剧本并回灌导出最终 `.scn`（`v0.3.0-alpha` Release 目前仍是 `v0.9.60` 底子构建的初版西西里小剧本）。

---

## [v0.3.0-alpha] - 2026-11-25（首个可玩西西里小剧本发布包 `Italy_Husky_43`）

### 新增产出
- **可玩剧本文件**：产出并通过编辑器保存 [Dat/Scen/Italy_Husky_43.scn](Dat/Scen/Italy_Husky_43.scn)（约 2.14 MB）及配套选剧本英文简介 [Dat/Scen/Italy_Husky_43.txt](Dat/Scen/Italy_Husky_43.txt)。
- **发布校验与压缩包**：生成 [SHA256SUMS.txt](SHA256SUMS.txt)，并构建可解压即用的发布压缩包 `Italy_Husky_43-v0.3.0-alpha.zip`（挂至 GitHub Release `v0.3.0-alpha`）。
- **仓库规则与说明**：更新 `.gitignore` 显式放行 `Dat/Scen/*.scn` 与 `Dat/Scen/*.txt`，并在 `README.md` 新增下载安装指引。

### 已完成实机编辑器验证
- **WitE2 v1.05.02 New Editor 批量导入**：20 个裁剪 CSV 全量 `Import from CSV` 通过，报告 **`Errors: 0, Warnings: 4`**（4 条警告为上游 `OBs.csv` 原有空槽提示）。
- **编辑器内置 Scenario Check Utility**：核对 **0 越界（Off-Map）、0 超堆叠（Overstack）**；其余提示均为上游 `WITW+WITE` 盟军套苏联皮必然产生的国籍/班组与机动差异常规项。

### 待实机游玩验证
- 游戏内新开 `Italy_Husky_43` 实测 T1 盟军两栖 `INVADE` 与 `F9 → Airborne` 落地、过回合速度及平衡性；
- 大剧本 `Italy_Campaign_43_45` 编辑器回灌保存与发布。

---

## [v0.2.0] - 2026-11-25（适配 New Editor 20 文件格式、真数据跑通裁剪与 `wite2_tools` 协作）

### 重大发现与修正
- **适配 WitE2 v1.05.02 New Editor 导出格式**：实机导出 `Dat/CSV/WITW+WITE v0.9.60/` 后确认其为 20 个 PascalCase 文件子目录（含变长 `<cnd>/<actSet>` 尾列的 `GameEvents.csv` 及含 `ISO-8859-1` 字符的 `Pilots.csv`），已升级 `crop_csv.py` 与 `validate_csv.py` 全面兼容双格式并原编码无损写回。
- **修复 `HQ=5` 机场零坐标问题**：`Units.csv` 中所有机场 `X=0, Y=0`，改为先扫描 `Locations.csv` 的 `AbUnit` 反查机场真实地图坐标，成功保住西西里 `55` 座机场（`159` 航空队）与大剧本 `173` 座机场（`241` 航空队）。
- **修正北非集结港西界并引入 `exclude_boxes`**：实测盟军 `AFHQ (86,295)`、第 1/45 师与 TF81/TF85/TF86 分布在 `X=59..150`，将大剧本与西西里剧本 `NW_x` 西延至 `57`，同时用 `exclude_boxes` 精准剔除南法/西班牙、巴尔干与撒丁岛南缘无关单位。
- **支持 `GameEvents.csv` 自动停用无关事件**：按列表流式读写，只改 `evActive` 列，自动停用柏林陷落（`id=78`）、东线/北欧事件及西西里小剧本中的 `Italy Surrenders (id=24)`。

### 新增产出与文档
- 新增真实裁剪审计报告：[docs/HUSKY_REAL_CROP_REPORT.md](docs/HUSKY_REAL_CROP_REPORT.md) 与 [docs/CAMPAIGN_REAL_CROP_REPORT.md](docs/CAMPAIGN_REAL_CROP_REPORT.md)（对应待导入成品位于本地 `output/Italy_Husky_43/` 与 `output/Italy_Campaign_43_45/`，不推大文件上 Git）。
- 在 [AI_DEV_GUIDE.md](AI_DEV_GUIDE.md) 补充第 15~19 条实测避坑经验及与开源工具 `mlshort/wite2_tools` 的联合体检工作流；更新 [docs/EDITOR_WORKFLOW.md](docs/EDITOR_WORKFLOW.md) 为 New Editor 紫色 `CSV` 标签页精确操作流程。

### 已完成验证（自动化与真实 `v0.9.60` 数据）
- 运行 `python -m unittest discover -s tests -v`：**8/8 测试全部通过**（含真实 `Dat/CSV/WITW+WITE v0.9.60/` 端到端裁剪与校验、`Pilots.csv` SHA256 原字节一致、`GameEvents.csv` 变长每行列数不变、排除区存活单位为 0）。
- 运行 `validate_csv.py` 校验 `Italy_Husky_43`（424 单位 / 55 机场 / 159 航空队）与 `Italy_Campaign_43_45`（729 单位 / 173 机场 / 241 航空队）：均返回 **`errors: []`、`overstack_hexes: 0`、`husky_geometry_errors: 0`**。

### 待实机验证（下一里程碑 `v0.3.0` 目标）
- 将 `output/Italy_Husky_43/` 与 `output/Italy_Campaign_43_45/` 在 WitE2 New Editor 中执行 `Import from CSV`、`Main Tab` 边界设置与 `DAMAGE OFF-MAP RAIL`，保存为 `.scn` 并在游戏中实测 T1~T2 登陆、空降与回合演算速度。

---

## [v0.1.0] - 2026-11-25（初始化工程、裁剪工具链与 AI 避坑指南）

### 新增内容
- 初始化 `意大利mod/` 独立工程与只读上游基线 `source/witw-wite-v0.9.60/`（已 `.gitignore`）。
- 编写三大纯意大利剧本配置 `config/*.json`、上游数据提炼脚本 `tools/analyze_upstream_italy.py`、`shape2` 六角格几何模块 `tools/hex_geometry.py`、旧版 CSV 裁剪与校验工具及 `AI_DEV_GUIDE.md`。
- 运行 `python -m unittest discover -s tests -v`：初版 6/6 测试全部通过，并创建 GitHub 仓库 `TinMinL/wite2-italy-mod`。
