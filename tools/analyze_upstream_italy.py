#!/usr/bin/env python3
"""从 WITW+WITE v0.9.60 上游数据中提炼纯意大利/地中海战区基线与审计报告。

输出：
- data/italy_extracted_baseline.json
- docs/ITALY_BASELINE_AUDIT.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MOD_ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_DATA = MOD_ROOT / "source" / "witw-wite-v0.9.60" / "data"
CONFIG_DIR = MOD_ROOT / "config"
OUT_JSON = MOD_ROOT / "data" / "italy_extracted_baseline.json"
OUT_MD = MOD_ROOT / "docs" / "ITALY_BASELINE_AUDIT.md"

ITALY_KEYWORDS = (
    "italy", "italian", "sicily", "husky", "salerno", "anzio", "naples",
    "rome", "foggia", "messina", "palermo", "taranto", "bari", "tunis",
    "bizerte", "malta", "valletta", "mediterranean", "masaf", "maaf",
    "nataf", "nasaf", "afhq", "15th army group", "fifth us army",
    "eighth british army", "corsica", "sardinia", "cagliari", "gela",
    "syracuse", "catania", "509th", "82nd", "1st british airborne",
    "hermann goering", "15th panzer grenadier", "bersaglieri",
)


def load_json(name: str) -> Any:
    path = UPSTREAM_DATA / name
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def in_bounds(xy: list[int] | tuple[int, int] | None, nw: list[int], se: list[int]) -> bool:
    if not xy or len(xy) < 2:
        return False
    x, y = int(xy[0]), int(xy[1])
    return nw[0] <= x < se[0] and nw[1] <= y < se[1]


def matches_italy_text(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in ITALY_KEYWORDS)


def main() -> None:
    campaign_cfg = json.loads((CONFIG_DIR / "italy_campaign_43_45.json").read_text(encoding="utf-8"))
    husky_cfg = json.loads((CONFIG_DIR / "italy_husky_43.json").read_text(encoding="utf-8"))

    camp_nw, camp_se = campaign_cfg["map_nw_limit"], campaign_cfg["map_se_limit"]
    husky_nw, husky_se = husky_cfg["map_nw_limit"], husky_cfg["map_se_limit"]

    vp_data = load_json("victory-points.json")
    husky_fix = load_json("husky-coastline-fix.json")
    husky_hist = load_json("husky-landing-history.json")
    husky_air = load_json("husky-airborne-targets.json")
    husky_open = load_json("husky-opening.json")
    reinf = load_json("reinforcements.json")
    axis_res = load_json("axis-reserve-releases.json")
    manpower = load_json("manpower.json")
    logistics = load_json("logistics.json")
    commanders = load_json("commanders.json")
    opening_stocks = load_json("opening-stocks.json")

    # 1. 胜利点城市筛查
    italy_vps: list[dict[str, Any]] = []
    for key in ("previous28_added_objectives", "revised52_industrial_objectives", "new24_eastern_objectives"):
        for item in vp_data.get(key, []):
            xy = item.get("xy")
            if item.get("region") == "Italy" or in_bounds(xy, camp_nw, camp_se):
                italy_vps.append({**item, "source_group": key})

    # 2. 地面/HQ增援筛查（按坐标落入意大利大剧本可玩区，或名称匹配地中海关键词）
    ground_records = reinf.get("ground", [])
    ground_in_camp = []
    ground_in_husky = []
    ground_keyword_only = []
    for rec in ground_records:
        xy = rec.get("xy")
        name = str(rec.get("name", ""))
        if in_bounds(xy, camp_nw, camp_se):
            ground_in_camp.append(rec)
            if in_bounds(xy, husky_nw, husky_se):
                ground_in_husky.append(rec)
        elif matches_italy_text(name):
            ground_keyword_only.append(rec)

    # 3. 航空增援（没有直接 xy，按名称关键词筛查仅供参考）
    air_records = reinf.get("air", [])
    air_med_named = [rec for rec in air_records if matches_italy_text(str(rec.get("name", "")))]

    # 4. 轴心预备队解锁列表中的意大利关联项
    axis_changes = axis_res.get("changes", [])
    axis_italy_changes = [
        item for item in axis_changes
        if matches_italy_text(json.dumps(item, ensure_ascii=False))
        or in_bounds(item.get("xy"), camp_nw, camp_se)
    ]

    # 5. 将领任命（筛选地中海/意大利相关）
    italy_commanders = [
        item for item in commanders.get("appointments", [])
        if matches_italy_text(json.dumps(item, ensure_ascii=False))
    ]

    # 6. 开局库存修复中涉及哈士奇/地中海主力师的样本
    opening_stock_samples = [
        rec for rec in opening_stocks.get("records", [])
        if matches_italy_text(str(rec.get("name", ""))) or in_bounds(rec.get("xy"), camp_nw, camp_se)
    ]

    extracted = {
        "upstream_version": "WITW+WITE v0.9.60",
        "campaign_bounds": {"nw": camp_nw, "se": camp_se},
        "husky_bounds": {"nw": husky_nw, "se": husky_se},
        "victory_points": {
            "italy_city_count": len(italy_vps),
            "italy_base_vp_sum": sum(int(x.get("base_vp", 0)) for x in italy_vps),
            "cities": italy_vps,
        },
        "husky": {
            "board_shape": husky_fix.get("board_shape"),
            "root_cause": husky_fix.get("root_cause"),
            "landings": husky_fix.get("landings"),
            "airborne_plans": husky_fix.get("airborne_plans"),
            "assault_divisions": husky_hist.get("assault_divisions"),
            "independent_brigades": husky_hist.get("independent_brigades"),
            "hq_relocations": husky_open.get("hq_relocations"),
            "airborne_eligibility_note": husky_air.get("native_eligibility"),
        },
        "reinforcements_summary": {
            "total_upstream_ground": len(ground_records),
            "ground_with_xy_in_italy_campaign_bounds": len(ground_in_camp),
            "ground_with_xy_in_husky_bounds": len(ground_in_husky),
            "ground_keyword_only_outside_bounds": len(ground_keyword_only),
            "total_upstream_air": len(air_records),
            "air_med_keyword_matches": len(air_med_named),
            "note": "许多盟军未来增援先进入英国/北非兼容落点，因此按坐标筛出的是直接标定意大利/突尼斯/马耳他落点的子集；完整筛选需在 Export CSV 后由 crop_csv.py 结合 HQ 链与基地坐标判定。",
            "sample_ground_in_bounds": ground_in_camp[:30],
        },
        "axis_reserves": {
            "total_changes_records": len(axis_changes),
            "italy_related_records": axis_italy_changes,
        },
        "commanders_italy_related": italy_commanders,
        "opening_stocks_italy_samples_count": len(opening_stock_samples),
        "manpower_and_logistics_baseline": {
            "upstream_allied_total_allowance": manpower.get("total_allowance"),
            "upstream_allied_initial_allowance": manpower.get("initial_allowance"),
            "upstream_logistics_stages": logistics.get("stages"),
            "italy_only_scaling_note": "上游数值覆盖西欧+地中海双线；纯意大利战役需在编辑器中按战区兵力比例下调至约 25%~35%，并为已移除德国本土工厂后的轴心方补充战区月度人力事件。",
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(extracted, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# 上游 WITW+WITE v0.9.60 意大利战区基线审计报告",
        "",
        "> 本文件由 `tools/analyze_upstream_italy.py` 自动从 `source/witw-wite-v0.9.60/data/*.json` 提炼生成，供人类与 AI 开发时速查。",
        "",
        "## 1. 地图裁剪口径对比",
        f"- **全欧底图**：`378 × 355 = 134,190` 格",
        f"- **意大利战役大剧本** (`NW={camp_nw}, SE={camp_se}`): 有效范围 `X:[{camp_nw[0]}..{camp_se[0]-1}]`, `Y:[{camp_nw[1]}..{camp_se[1]-1}]` = `{(camp_se[0]-camp_nw[0])*(camp_se[1]-camp_nw[1]):,}` 格（削减 `94.10%`）",
        f"- **哈士奇西西里小剧本** (`NW={husky_nw}, SE={husky_se}`): 有效范围 `X:[{husky_nw[0]}..{husky_se[0]-1}]`, `Y:[{husky_nw[1]}..{husky_se[1]-1}]` = `{(husky_se[0]-husky_nw[0])*(husky_se[1]-husky_nw[1]):,}` 格（削减 `98.60%`）",
        "",
        "## 2. 上游意大利胜利点目标（从 `victory-points.json` 提炼）",
        f"- 命中数量：**{len(italy_vps)}** 座城市，上游基础分合计：**{extracted['victory_points']['italy_base_vp_sum']}**",
        "",
        "| 城市 | ID | 坐标 (X, Y) | 上游基础分 | 备注 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in italy_vps:
        md_lines.append(f"| {c.get('city')} | {c.get('id')} | ({c['xy'][0]}, {c['xy'][1]}) | {c.get('base_vp')} | {c.get('source_group')} |")

    md_lines.extend([
        "",
        "## 3. 哈士奇行动已验证坐标（`board_shape = 2` 按行奇偶错位）",
        f"- **曾踩坑内陆格**：`{husky_fix.get('old_inland_target')}`（不要将其当作登陆海滩，仅作 `3/82nd` 空降目标）",
        f"- **修正后 TF81 海滩**：`{husky_fix.get('new_beach')}`，出海格：`{husky_fix.get('new_approach')}`",
        "",
        "### 两栖登陆编组 (6 支)",
        "| TF ID | 登陆目标 (X, Y) | 出海海格 (X, Y) |",
        "| --- | --- | --- |",
    ])
    for tf_id, info in husky_fix.get("landings", {}).items():
        md_lines.append(f"| {tf_id} | {tuple(info['target'])} | {tuple(info['sea_approach'])} |")

    md_lines.extend([
        "",
        "### 空降预案 (7 支分队)",
        "| 单位 ID | 目标 (X, Y) | 支援 TF | 说明 |",
        "| --- | --- | --- | --- |",
    ])
    for p in husky_fix.get("airborne_plans", []):
        md_lines.append(f"| {p['id']} | {tuple(p['target'])} | {p['supporting_tf']} | {p['role']} |")

    md_lines.extend([
        "",
        "## 4. 增援与后勤基线统计（注意统计口径）",
        f"- 上游地面增援总记录：`{len(ground_records)}` 条；其中落点坐标直接位于意大利大剧本框内的有 `{len(ground_in_camp)}` 条（哈士奇框内 `{len(ground_in_husky)}` 条），另有 `{len(ground_keyword_only)}` 条关键词命中但初始落点在英国/北非外侧。",
        f"- 上游航空增援总记录：`{len(air_records)}` 条；按地中海关键词匹配 `{len(air_med_named)}` 条（实际按所在机场归属裁剪，详见 `tools/crop_csv.py`）。",
        f"- 轴心预备队调整中涉及意大利关键词/坐标的记录：`{len(axis_italy_changes)}` / `{len(axis_changes)}` 条。",
        f"- 盟军人力拨款上游基线：首笔 `{manpower.get('initial_allowance'):,}`，全欧双线总计 `{manpower.get('total_allowance'):,}`（纯意大利战役需缩放到约 25%~35%）。",
        "",
    ])
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Generated {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
