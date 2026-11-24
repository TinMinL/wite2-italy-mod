# 更新日志 (`CHANGELOG.md`)

所有重要变更、工具链验证范围与待实机核对项均记录在此。

---

## [v0.1.0] - 2026-11-25（初始化工程、裁剪工具链与 AI 避坑指南）

### 新增内容
- **工程基线**：在独立 `意大利mod/` 目录完成初始化，本地解压 `WITW-WITE-v0.9.60.zip` 至只读 `source/` 目录（已通过 `.gitignore` 排除上游二进制与游戏本体文件，避免污染游戏目录及仓库）。
- **三大纯意大利剧本配置 (`config/`)**：
  - `italy_campaign_43_45.json`：1943–1945 意大利战役大剧本（`NW=[104,208]`, `SE=[176,318]`，有效 `7,920` 格，削减 `94.10%`，`96` 回合，非 Campaign 模式）。
  - `italy_husky_43.json`：1943 哈士奇西西里登陆小剧本（`NW=[118,275]`, `SE=[166,314]`，有效 `1,872` 格，削减 `98.60%`，`8` 回合，含 6 登陆+7 空降校验规则）。
  - `italy_avalanche_rome.json`：1943–1944 萨莱诺至罗马中小型剧本蓝图（`NW=[122,246]`, `SE=[172,296]`，有效 `2,500` 格，削减 `98.14%`，`40` 回合）。
- **Python 裁剪与校验工具链 (`tools/`)**：
  - `analyze_upstream_italy.py`：从上游 `data/*.json` 自动提取纯意大利基线至 `data/italy_extracted_baseline.json` 与 `docs/ITALY_BASELINE_AUDIT.md`。
  - `hex_geometry.py`：实现 WitE2 原生 `shape2`（按行错位）邻接/距离函数及半开区间 `[NW, SE)` 边界判定，并保留 `shape3` 反例回归对照。
  - `crop_csv.py`：实现不删行保槽位的 CSV 裁剪（置空框外单位为 `delay=998`、清零框外城市工业与库存、清理 `theaterBox`/`thBoxLock`、支持 `--relocate-offmap-hqs` 自动迁入高司锚点、输出 JSON + Markdown 审计报告）。
  - `validate_csv.py`：实现 6 项离线检查（Schema、边界、HQ 链、堆叠、机场链接、Husky `shape2` 几何）。
- **文档体系（人类 + AI 通用）**：
  - `AI_DEV_GUIDE.md`：包含项目架构铁律、WitE2 引擎核心机制、从上游继承的 14 条血泪避坑清单及 AI Quickstart。
  - `docs/SCENARIO_BLUEPRINT.md`、`docs/EDITOR_WORKFLOW.md`、`README.md`。

### 已完成验证（静态与自动化）
- 运行 `python tools/analyze_upstream_italy.py`：成功生成 `data/italy_extracted_baseline.json`（含 16 座框内目标城市、6 支两栖编组与 7 支空降分队信息）与 `docs/ITALY_BASELINE_AUDIT.md`。
- 运行 `python -m unittest discover -s tests -v`：**6/6 测试全部通过**（`shape2` 与上游 `husky-coastline-fix.json` 逐格匹配；官方 `Introductory Scenario 1 - Velikie Luki` CSV 端到端裁剪保留全部 `16,384` 单位槽位与表头、正确迁移框外 HQ 并通过 `validate_csv.py` 零报错校验）。

### 待实机验证（下一里程碑 `v0.2.0` 目标）
- 在本地 `WarInTheEast2.exe` 编辑器中打开 `WITW+WITE v0.9.60.scn` 执行 `Export CSV` → 运行 `crop_csv.py` → `Import CSV` → 完成 `Main Tab` 与 `DAMAGE OFF-MAP RAIL` 后另存首个可玩 `.scn`（优先 `Italy_Husky_43.scn`），并实机推进 T1~T2 验证登陆、空降与回合演算速度。
