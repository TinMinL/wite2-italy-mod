# 更新日志 (`CHANGELOG.md`)

所有重要变更、工具链验证范围与待实机核对项均记录在此。

---

## [v0.4.0] - 2026-11-25（正式切换 `WITW+WITE v0.9.65` + 恢复 36 支法国/预备队德军大修）

### 重大改进
- **正式切换上游母版至 `WITW+WITE v0.9.65`**：下载、SHA256 校验（`a437b391...`）并在 New Editor 导出 `Dat/CSV/WITW+WITE v0.9.65/`。相比 `v0.9.60`，西西里航空队增至 `185`（轴心翻倍至 `22`），大剧本航空队跃升至 `337`（含 `205` 座机场、威尼斯铁路司令部、41 座仓库与 2,338 名轴心飞行员）。
- **彻底补齐大剧本德军法国/奥地利/`TB=7` 增援与直属支援营（共 36 支）**：基于本地官方 WITW `Battleground Italy 43-45` CSV 逐一核对 ID，大剧本北界北延至 `Y=202`（`NW=[57,202], SE=[176,318]`），通过 `force_keep_units` 恢复 5 支集团军/军部（含第 10/14 集团军、LXXVI/LXXV/XI 军）、21 支主力师旅（含第 26 装、1/2/4 伞兵师、44/65/71/92/98/232/305/334/356/710/715 步兵师、第 5 山地、42/114 猎兵、20 空军野战师，且修正 4 伞兵师为 `Delay=27` 增援）与 10 支精锐重坦/重驱/突击炮支援营（含 508 虎式营、653 象式营、242/907/914/11 伞兵突击炮营等），全部清 `TheaterBox=0` 并挂载至 `3240 (Army Group C)`。
- **裁剪引擎增强 (`tools/crop_csv.py`)**：`force_keep_units` 新增 `higher_hq` 与 `theater_box` 覆写字段；修复延迟增援祖先 HQ 在向上闭包时未重定位 `ArriveX/ArriveY` 的缺陷。
- **西西里小剧本历史校准 (`italy_husky_43.json`)**：北界移至 `Y=270` 找回第 29 装掷师 (`631`)，豁免第 1 伞兵师 (`2044` 挂载 `77 XIV Pz Corps`) 于 T2 空运卡塔尼亚，冻结 11 支萨莱诺盟军师（`Frozen=12`），德意核心师士气按官方 WITW `Operation Husky` 回调。
- **新增 WITW 对照脚本与报告**：[tools/compare_witw_husky.py](tools/compare_witw_husky.py) 与 [docs/WITW_HUSKY_COMPARISON.md](docs/WITW_HUSKY_COMPARISON.md)。

### 新增产出与实机编辑器验证（`v0.4.0` 双剧本发版）
- **双可玩剧本文件已导入保存**：
  - [Dat/Scen/Italy_Husky_43.scn](Dat/Scen/Italy_Husky_43.scn)（`2,201,048` 字节，8 回合西西里小剧本）；
  - [Dat/Scen/Italy_Campaign_43_45.scn](Dat/Scen/Italy_Campaign_43_45.scn)（`2,205,863` 字节，96 回合意大利全战役大剧本）。
  - 两份剧本均已在 **WitE2 v1.05.02 New Editor** 完成 20 文件 CSV 批量 `Import from CSV`（均报告 **`Batch import: Errors: 0, Warnings: 4`**，4 条为上游 `OBs.csv` 原有空槽提示）、Main Tab 边界与非 Campaign 胜利条件设定，以及 New Editor 铁路/港口初始化后保存。
- **中英双语剧本简介**：
  - 默认纯 ASCII 英文简介：[Dat/Scen/Italy_Husky_43.txt](Dat/Scen/Italy_Husky_43.txt) 与 [Dat/Scen/Italy_Campaign_43_45.txt](Dat/Scen/Italy_Campaign_43_45.txt)（适配未装汉化的原版游戏）；
  - 中文 UTF-8 BOM 简介：[Dat/Scen_ZH/Italy_Husky_43.txt](Dat/Scen_ZH/Italy_Husky_43.txt) 与 [Dat/Scen_ZH/Italy_Campaign_43_45.txt](Dat/Scen_ZH/Italy_Campaign_43_45.txt)（适配 `WITE2_CN_10502` 等中文汉化环境）。
- **自动化验证**：`python -m unittest discover -s tests -v` 8/8 测试全部通过（直接跑在 `Dat/CSV/WITW+WITE v0.9.65/` 上，含全部 36 支德军历史增援断言）；`validate_csv.py` 对 `Italy_Husky_43`（435 单位 / 61 机场 / 185 航空队）与 `Italy_Campaign_43_45`（810 单位 / 205 机场 / 337 航空队）均返回 **`errors: []`、`overstack_hexes: 0`、`husky_geometry_errors: 0`**。
- **校验与发布包**：已更新 [SHA256SUMS.txt](SHA256SUMS.txt) 覆盖上述 6 份交付文件，打包 `wite2-italy-mod-v0.4.0.zip` 并发布至 GitHub Release `v0.4.0`。

### 待实机游玩验证
- 进入正式游戏测试 T1~T2 两栖 `INVADE`、空降落地、大剧本德军增援按期到达与回合演算速度。

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
