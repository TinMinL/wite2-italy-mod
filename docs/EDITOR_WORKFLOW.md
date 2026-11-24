# WitE2 编辑器操作与 CSV 往返流水线指南 (`EDITOR_WORKFLOW.md`)

> 本流程确保**绝对不破坏游戏原版目录**，并把所有批量数据裁剪交给 Python 完成，只把无法经 CSV 往返的设定留给 WitE2 编辑器 UI。

---

## 第 0 步：准备工作（一次性）

1. 确认游戏根目录 `Dat\Scen\` 下已备份原文件；将 `意大利mod\source\witw-wite-v0.9.60\Dat\Scen\WITW+WITE v0.9.60.scn` 和 `.txt` 复制到游戏 `Dat\Scen\`（或先另存为工作副本如 `Italy_Base_Work.scn`）。
2. 打开 `WarInTheEast2.exe` → **Editor** → 载入 `WITW+WITE v0.9.60.scn`。
3. 点击菜单导出全套 CSV：**`Export CSV`**（WitE2 会将全套 `*_unit.csv`、`*_airgroup.csv`、`*_city.csv` 等导出到游戏 `Dat\CSV\` 目录）。

---

## 第 1 步：用 Python 工具链裁剪并离线校验（以西西里小剧本 `italy_husky_43` 为例）

在 `意大利mod` 目录下运行（先 `--dry-run` 预演，确认无误再实际输出）：

```powershell
# 1. 试跑（不写文件，仅看审计统计与待迁移 HQ）
python tools/crop_csv.py `
  --input-dir "..\Dat\CSV" `
  --prefix "WITW+WITE v0.9.60" `
  --config "config\italy_husky_43.json" `
  --output-dir "output\husky_csv" `
  --dry-run `
  --relocate-offmap-hqs `
  --report "output\husky_crop_report.md"

# 2. 正式生成裁剪后 CSV
python tools/crop_csv.py `
  --input-dir "..\Dat\CSV" `
  --prefix "WITW+WITE v0.9.60" `
  --config "config\italy_husky_43.json" `
  --output-dir "output\husky_csv" `
  --relocate-offmap-hqs `
  --report "output\husky_crop_report.md"

# 3. 执行 6 项离线校验（必须返回 PASS 或仅可接受的 WARN，errors 必须为空）
python tools/validate_csv.py `
  --input-dir "output\husky_csv" `
  --prefix "WITW+WITE v0.9.60" `
  --config "config\italy_husky_43.json"
```

---

## 第 2 步：将裁剪后的 CSV 导入 WitE2 编辑器

1. 将 `output\husky_csv\WITW+WITE v0.9.60_*.csv` 复制回游戏 `Dat\CSV\`（**强烈建议先备份原导出的 CSV**）。
2. 在 WitE2 编辑器中另存一份新剧本（如 `Italy_Husky_43_Work.scn`），避免覆盖母版。
3. 在编辑器中点击 **`Import CSV`**，载入裁剪后的数据。

---

## 第 3 步：编辑器内必需的收尾操作（CSV 无法替代的部分）

按以下顺序在编辑器内逐项完成：

1. **`Main Tab`（核心参数）**：
   - 修改剧本名称与保存文件名（例如 `Italy_Husky_43` / `Italy_Campaign_43_45`）。
   - 关闭 **Campaign** 模式（确保使用非 Campaign 胜负结算，避免柏林陷落硬编码）。
   - 设置 **`Turns`**（`8` 或 `96`）。
   - 设置 **`Map NW Limit`** 与 **`Map SE Limit`**（填入配置文件中数值，例如 Husky 填 `118, 275` 与 `166, 314`）。
   - 检查/设置自定义胜利点阈值（Victory Conditions）与起始船运池（Ladoga 栏）。
2. **`Events Tab`（事件清理）**：
   - 删除或停用东线、诺曼底、巴尔干、罗马尼亚投降、柏林陷落等无关事件。
   - **小剧本 (`italy_husky_43`)** 停用 1943.9.8 意大利停战事件。
   - **大剧本 (`italy_campaign_43_45`)** 调整盟军人力拨款金额（约 50~70 万）并补足德军意大利战区月度人力拨款。
3. **`Locations / City` 微调**：
   - 将矩形盒西北/东北角上不属于意大利战区的南法/巴尔干城市 VP 设回 `0`。
4. **`Editor Utilities` 必跑四步**：
   - 执行 **`DAMAGE OFF-MAP RAIL`**（破坏所有框外铁路，彻底切断框外补给寻路开销）。
   - 执行 **`INIT RAIL/PORT VALUES`**（重新初始化框内海域港口吞吐量与铁路容量）。
   - 执行 **`RESET UNIT SUPPORT VALUES`**（如修改过编制或库存）。
   - 执行 **`SCENARIO CHECK UTILITY`**（逐项确认无 `Bad HQ Errors`、`Off-Map Arrival Errors`、`Overstack Errors`）。

---

## 第 4 步：实机验证清单（每次发版前必做）

1. 新开局进入游戏（不要读旧存档），确认小地图与相机被正确限制在 `NW..SE` 区域内，无框外异常镜头跳变。
2. 检查 **T1 盟军阶段**：打开 `F9 → Airborne` 和两栖 HQ `INVADE` 按钮，确认哈士奇登陆与空降全部合法可用。
3. 跑完 **T1 结束 → T2 后勤战报**：确认回合运算耗时明显下降、前线补给/燃油正常流动、无崩溃或苏制武器误补。
4. 只有通过实机验证的 `.scn` 与 `.txt`，才在 `CHANGELOG.md` 中标记为“实机已验证”。
