# 更新日志 (`CHANGELOG.md`)

所有重要变更、工具链验证范围与待实机核对项均记录在此。

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
