#!/usr/bin/env python3
"""WitE2 裁剪后 CSV 离线校验器（兼容 New Editor 20 文件与 Old Editor 前缀格式）。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from crop_csv import (
    _to_int,
    detect_csv_encoding,
    detect_editor_layout,
    is_airgroup_slot_alive,
    is_unit_slot_alive,
    read_csv_rows,
)
from hex_geometry import is_hex_included, validate_husky_geometry

OLD_UNIT_COLS = {"id", "name", "type", "nat", "player", "x", "y", "ax", "ay", "delay", "hq", "hhq"}
OLD_AIR_COLS = {"id", "name", "player", "base", "startBase", "delay"}
OLD_CITY_COLS = {"id", "name", "x", "y", "portValue", "abUnit"}

NEW_UNIT_COLS = {"ID", "Name", "Nation", "Type", "Player", "X", "Y", "ArriveX", "ArriveY", "HQ", "HigherHQ", "Delay"}
NEW_AIR_COLS = {"ID", "Name", "Player", "Base", "StartBase", "Delay"}
NEW_CITY_COLS = {"ID", "Name", "X", "Y", "PortValue", "AbUnit"}


def validate_scenario_csvs(
    input_dir: Path,
    prefix: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """执行离线校验并返回结构化结果。"""
    nw = config["map_nw_limit"]
    se = config["map_se_limit"]
    exclude_boxes = config.get("exclude_boxes", [])
    errors: list[str] = []
    warnings: list[str] = []

    try:
        layout = detect_editor_layout(input_dir, prefix)
    except FileNotFoundError as exc:
        return {"status": "FAIL", "errors": [f"[Schema] {exc}"], "warnings": [], "stats": {}}

    if layout == "new":
        u_fields, u_rows, _ = read_csv_rows(input_dir / "Units.csv")
        a_fields, a_rows, _ = read_csv_rows(input_dir / "AirGroups.csv")
        c_fields, c_rows, _ = read_csv_rows(input_dir / "Locations.csv")
        req_u, req_a, req_c = NEW_UNIT_COLS, NEW_AIR_COLS, NEW_CITY_COLS
        k = {
            "id": "ID", "name": "Name", "player": "Player", "x": "X", "y": "Y",
            "ax": "ArriveX", "ay": "ArriveY", "delay": "Delay", "hq": "HQ", "hhq": "HigherHQ",
            "ab_id": "ID", "ab_name": "Name", "base": "Base", "startBase": "StartBase",
            "abUnit": "AbUnit",
        }
    else:
        u_fields, u_rows, _ = read_csv_rows(input_dir / f"{prefix}_unit.csv")
        a_fields, a_rows, _ = read_csv_rows(input_dir / f"{prefix}_airgroup.csv")
        c_fields, c_rows, _ = read_csv_rows(input_dir / f"{prefix}_city.csv")
        req_u, req_a, req_c = OLD_UNIT_COLS, OLD_AIR_COLS, OLD_CITY_COLS
        k = {
            "id": "id", "name": "name", "player": "player", "x": "x", "y": "y",
            "ax": "ax", "ay": "ay", "delay": "delay", "hq": "hq", "hhq": "hhq",
            "ab_id": "id", "ab_name": "name", "base": "base", "startBase": "startBase",
            "abUnit": "abUnit",
        }

    # 1. Schema 完整性
    for label, fields, req in (("Units", u_fields, req_u), ("AirGroups", a_fields, req_a), ("Locations", c_fields, req_c)):
        miss = req - set(fields)
        if miss:
            errors.append(f"[Schema] {label} 缺失列: {sorted(miss)}")
    if errors:
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "stats": {}}

    # 建立 Locations.AbUnit -> (x, y) 索引（New Editor 机场在 Units.csv 中 X=0,Y=0）
    ab_unit_xy: dict[str, tuple[int, int]] = {}
    for crow in c_rows:
        ab_id = str(_to_int(crow.get(k["abUnit"])))
        if ab_id != "0":
            ab_unit_xy[ab_id] = (_to_int(crow.get(k["x"])), _to_int(crow.get(k["y"])))

    unit_by_id: dict[str, dict[str, str]] = {r[k["id"]]: r for r in u_rows if r.get(k["id"])}
    alive_units = [r for r in u_rows if is_unit_slot_alive(r)]
    alive_ids = {r[k["id"]] for r in alive_units}

    # 2. 边界校验 + 3. HQ 链校验 + 4. 单格堆叠
    off_map_units: list[str] = []
    bad_hq_links: list[str] = []
    hex_stacks: dict[tuple[int, int, int], list[str]] = defaultdict(list)

    for row in alive_units:
        uid = row[k["id"]]
        name = row.get(k["name"], "")
        player = _to_int(row.get(k["player"]))
        x, y = _to_int(row.get(k["x"])), _to_int(row.get(k["y"]))
        ax, ay = _to_int(row.get(k["ax"])), _to_int(row.get(k["ay"]))
        delay = _to_int(row.get(k["delay"]))
        hq_type = _to_int(row.get(k["hq"]))
        hhq = str(_to_int(row.get(k["hhq"])))

        if hq_type == 5 and uid in ab_unit_xy:
            lx, ly = ab_unit_xy[uid]
            if not is_hex_included(lx, ly, nw, se, exclude_boxes):
                off_map_units.append(f"AirBase {uid} ({name}) at Location ({lx},{ly}) outside bounds")
        elif x > 0 and y > 0:
            if not is_hex_included(x, y, nw, se, exclude_boxes):
                off_map_units.append(f"Unit {uid} ({name}) at ({x},{y}) outside bounds")
            if hq_type == 0:
                hex_stacks[(player, x, y)].append(f"{uid}:{name}")
        elif delay > 0 and ax > 0 and ay > 0:
            if not is_hex_included(ax, ay, nw, se, exclude_boxes):
                off_map_units.append(f"Reinforcement {uid} ({name}) arrives at ({ax},{ay}) outside bounds")

        if hhq == "0":
            if hq_type != 1:
                warnings.append(f"[HQ] Unit {uid} ({name}, hq_type={hq_type}) has HigherHQ=0")
        elif hhq not in alive_ids:
            bad_hq_links.append(f"Unit {uid} ({name}) -> dead/missing HigherHQ={hhq}")
        else:
            parent = unit_by_id[hhq]
            if _to_int(parent.get(k["player"])) != player:
                bad_hq_links.append(f"Unit {uid} ({name}, p={player}) -> cross-side HigherHQ={hhq} (p={parent.get(k['player'])})")
            if _to_int(parent.get(k["hq"])) == 0:
                warnings.append(f"[HQ] Unit {uid} ({name}) -> parent HigherHQ={hhq} ({parent.get(k['name'])}) has hq_type=0")

    overstacks = [
        f"Player {p} hex ({hx},{hy}) has {len(members)} combat units: {members}"
        for (p, hx, hy), members in sorted(hex_stacks.items())
        if len(members) > 3
    ]

    errors.extend(f"[Off-Map] {m}" for m in off_map_units)
    errors.extend(f"[Bad HQ] {m}" for m in bad_hq_links)
    for msg in overstacks:
        warnings.append(f"[Overstack] {msg}")

    # 5. 航空队基地校验
    alive_airgroups = [r for r in a_rows if is_airgroup_slot_alive(r)]
    bad_airbases: list[str] = []
    for ag in alive_airgroups:
        aid = ag[k["ab_id"]]
        aname = ag.get(k["ab_name"], "")
        base = str(_to_int(ag.get(k["base"])))
        start_base = str(_to_int(ag.get(k["startBase"])))
        target_base = base if base != "0" else start_base
        if target_base == "0":
            warnings.append(f"[AirBase] Airgroup {aid} ({aname}) has Base=0 and StartBase=0")
        elif target_base not in alive_ids:
            bad_airbases.append(f"Airgroup {aid} ({aname}) -> missing/disabled Base={target_base}")
        else:
            bunit = unit_by_id[target_base]
            if _to_int(bunit.get(k["hq"])) != 5:
                warnings.append(f"[AirBase] Airgroup {aid} ({aname}) -> unit {target_base} has HQ={bunit.get(k['hq'])} (expected 5)")
    errors.extend(f"[AirBase] {m}" for m in bad_airbases)

    # 6. GameEvents 策略核对（New Editor）
    events_path = input_dir / "GameEvents.csv"
    if layout == "new" and events_path.exists() and "events_policy" in config:
        policy = config["events_policy"]
        disable_ids = {str(x) for x in policy.get("disable_event_ids", [])}
        enc = detect_csv_encoding(events_path)
        with events_path.open("r", encoding=enc, newline="") as f:
            erows = list(csv.reader(f))
        if erows:
            active_idx = erows[0].index("evActive") if "evActive" in erows[0] else 12
            for row in erows[1:]:
                if len(row) > active_idx and row[0].strip() in disable_ids and row[active_idx].strip() == "1":
                    errors.append(f"[Events] Event {row[0]} ({row[1]}) should be disabled but evActive=1")

    # 7. Husky shape2 几何校验
    husky_errors: list[str] = []
    if "husky_validation" in config:
        husky_errors = validate_husky_geometry(config["husky_validation"])
        errors.extend(f"[Husky shape2] {m}" for m in husky_errors)

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {
        "status": status,
        "editor_layout": layout,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "total_unit_rows": len(u_rows),
            "alive_units": len(alive_units),
            "total_airgroup_rows": len(a_rows),
            "alive_airgroups": len(alive_airgroups),
            "total_city_rows": len(c_rows),
            "overstack_hexes": len(overstacks),
            "husky_geometry_errors": len(husky_errors),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="WitE2 裁剪 CSV 离线校验器")
    parser.add_argument("--input-dir", required=True, type=Path, help="待校验的 CSV 目录")
    parser.add_argument("--prefix", default="", help="Old Editor 前缀（New Editor 可留空）")
    parser.add_argument("--config", required=True, type=Path, help="剧本裁剪配置 JSON")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = validate_scenario_csvs(args.input_dir, args.prefix, config)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
