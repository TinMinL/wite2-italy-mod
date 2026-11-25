# WitE2 New Editor (v1.05.02) 导出与回灌流水线指南 (`EDITOR_WORKFLOW.md`)

> 本流程针对 **WitE2 v1.05.02 New Editor（20 文件子目录 CSV 格式）**，目前已直接为你生成好两套待导入的裁剪成品：
> - 西西里小剧本：`意大利mod\output\Italy_Husky_43\`
> - 意大利战役大剧本：`意大利mod\output\Italy_Campaign_43_45\`

---

## 第 0 步：在 New Editor 中导出母版 CSV（已完成时可跳过）

1. 将 `意大利mod\source\witw-wite-v0.9.60\Dat\Scen\WITW+WITE v0.9.60.scn` 和同名 `.txt` 复制到游戏 `Dat\Scen\`。
2. 启动 `WarInTheEast2.exe` → **Editor**（选 **New Editor**）→ **Load Scenario** 加载 `WITW+WITE v0.9.60`。
3. 切到最右侧紫色条纹的 **`CSV`** 标签页，全选后点击 **Export to CSV**。
4. 导出文件会落在游戏目录 `Dat\CSV\WITW+WITE v0.9.60\` 下（共 20 个 `.csv` 文件）。

---

## 第 1 步：用 Python 工具链生成与校验裁剪包（可随时按新配置重跑）

```powershell
# 西西里小剧本
python 意大利mod/tools/crop_csv.py `
  --input-dir "Dat/CSV/WITW+WITE v0.9.60" `
  --config "意大利mod/config/italy_husky_43.json" `
  --output-dir "意大利mod/output/Italy_Husky_43" `
  --relocate-offmap-hqs `
  --report "意大利mod/docs/HUSKY_REAL_CROP_REPORT.md"

python 意大利mod/tools/validate_csv.py `
  --input-dir "意大利mod/output/Italy_Husky_43" `
  --config "意大利mod/config/italy_husky_43.json"

# 意大利战役大剧本
python 意大利mod/tools/crop_csv.py `
  --input-dir "Dat/CSV/WITW+WITE v0.9.60" `
  --config "意大利mod/config/italy_campaign_43_45.json" `
  --output-dir "意大利mod/output/Italy_Campaign_43_45" `
  --relocate-offmap-hqs `
  --report "意大利mod/docs/CAMPAIGN_REAL_CROP_REPORT.md"

python 意大利mod/tools/validate_csv.py `
  --input-dir "意大利mod/output/Italy_Campaign_43_45" `
  --config "意大利mod/config/italy_campaign_43_45.json"
```

---

## 第 2 步：（可选）配合 `mlshort/wite2_tools` 做深度数据库体检

在导入前，可以额外用 `wite2_tools` 对 `意大利mod\output\Italy_Husky_43\` 跑一轮数据库一致性扫描（注意 `--nat-codes 1 3` 聚焦德意）：
```powershell
python -m wite2_tools.cli audit-batch --path "意大利mod\output\Italy_Husky_43"
python -m wite2_tools.cli gen-orphans --nat-codes 1 3
```

---

## 第 3 步：在 New Editor 中导入 CSV 并保存为独立 `.scn`（以西西里小剧本为例）

> ⚠️ **官方手册铁律**：点击 `Import from CSV` 前，务必关闭 Excel、VS Code 预览或任何打开了这些 `.csv` 的程序，否则编辑器会报 **`FAILED`**！

1. 在游戏 `Dat\CSV\` 下新建文件夹（或直接用工作剧本名，例如先在编辑器把 `WITW+WITE v0.9.60.scn` **另存为 `Italy_Husky_43.scn`**，记住不要覆盖母版！）。
2. 把 `意大利mod\output\Italy_Husky_43\` 里的 **20 个 `.csv` 文件** 全部复制到 `Dat\CSV\Italy_Husky_43\`（目录名须与你当前加载的 `.scn` 剧本名一致！如果刚才还没另存，可先在加载 `Italy_Husky_43` 后点一次 `Export to CSV` 让编辑器建出准确同名目录，再覆盖进去）。
3. 切到编辑器紫色 **`CSV`** 标签页，勾选全部分类（重点含 `Units`, `Locations`, `AirGroups`, `GameEvents`），点击 **`Import from CSV`**。

---

## 第 4 步：编辑器内必需的收尾操作（CSV 不涵盖的全局项）

1. **`Main Tab`**：
   - 确认关闭 **Campaign** 模式（避免柏林陷落硬编码）。
   - 设置 **`Turns`**：西西里小剧本填 `8`；意大利战役大剧本填 `96`。
   - 设置 **`Map NW Limit`** 与 **`Map SE Limit`**：
     - 西西里小剧本：`NW = 57, 275`，`SE = 166, 314`
     - 意大利战役大剧本：`NW = 57, 208`，`SE = 176, 318`
   - 调整船运池（UI 的 Ladoga 栏）与城市 VP 胜利条件。
2. **`Locations` 边角清零（大剧本推荐）**：检查非意大利的南法/巴尔干城市 VP 设为 `0`。
3. **运行编辑器内置清理与校验工具（Utility 必跑四步）**：
   - **`DAMAGE OFF-MAP RAIL`**（破坏全部框外铁路，断掉框外寻路开销）
   - **`INIT RAIL/PORT VALUES`**（刷新框内港口与铁路容量）
   - **`RESET UNIT SUPPORT VALUES`**
   - **`SCENARIO CHECK UTILITY`**（确认无致命报错）
4. 保存 `.scn` 与同名介绍 `.txt` 到游戏 `Dat\Scen\`，即可新开局实机测试！
