#!/usr/bin/env python3
"""WitE2 裁剪后 CSV 离线校验器（6 项结构、边界、指挥链、堆叠、机场与 shape2 几何校验）。"""

from __future__ import annotations

import argparse
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
    is_airgroup_slot_alive,
    is_unit_slot_alive,
    read_csv_rows,
)
from hex_geometry import in_playable_area, validate_husky_geometry

REQUIRED_UNIT_COLS = {"id", "name", "type", "nat", "player", "x", "y", "ax", "ay", "delay", "hq", "hhq"}
REQUIRED_AIR_COLS = {"id", "name", "player", "base", "startBase", "delay"}
REQUIRED_CITY_COLS = {"id", "name", "x", "y", "portValue", "abUnit"}


def validate_scenario_csvs(
    input_dir: Path,
    prefix: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """执行 6 项离线校验并返回结构化结果。"""
    nw = config["map_nw_limit"]
    se = config["map_se_limit"]

    errors: list[str] = []
    warnings: list[str] = []

    unit_path = input_dir / f"{prefix}_unit.csv"
    air_path = input_dir / f"{prefix}_airgroup.csv"
    city_path = input_dir / f"{prefix}_city.csv"

    for req in (unit_path, air_path, city_path):
        if not req.exists():
            errors.append(f"[Schema] 缺少文件: {req}")
            return {"status": "FAIL", "errors": errors, "warnings": warnings, "stats": {}}

    u_fields, u_rows = read_csv_rows(unit_path)
    a_fields, a_rows = read_csv_rows(air_path)
    c_fields, c_rows = read_csv_rows(city_path)

    # 1. Schema 完整性
    missing_u = REQUIRED_UNIT_COLS - set(u_fields)
    missing_a = REQUIRED_AIR_COLS - set(a_fields)
    missing_c = REQUIRED_CITY_COLS - set(c_fields)
    if missing_u:
        errors.append(f"[Schema] unit.csv 缺失列: {sorted(missing_u)}")
    if missing_a:
        errors.append(f"[Schema] airgroup.csv 缺失列: {sorted(missing_a)}")
    if missing_c:
        errors.append(f"[Schema] city.csv 缺失列: {sorted(missing_c)}")
    if errors:
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "stats": {}}

    unit_by_id: dict[str, dict[str, str]] = {r["id"]: r for r in u_rows if r.get("id")}
    alive_units = [r for r in u_rows if is_unit_slot_alive(r)]
    alive_ids = {r["id"] for r in alive_units}

    # 2. 可玩区边界校验 + 4. 单格堆叠统计
    off_map_units: list[str] = []
    bad_hq_links: list[str] = []
    hex_stacks: dict[tuple[int, int, int], list[str]] = defaultdict(list)

    for row in alive_units:
        uid = row["id"]
        name = row.get("name", "")
        player = _to_int(row.get("player"))
        x, y = _to_int(row.get("x")), _to_int(row.get("y"))
        ax, ay = _to_int(row.get("ax")), _to_int(row.get("ay"))
        delay = _to_int(row.get("delay"))
        hq_type = _to_int(row.get("hq"))
        hhq = str(_to_int(row.get("hhq")))

        if x > 0 and y > 0:
            if not in_playable_area(x, y, nw, se):
                off_map_units.append(f"Unit {uid} ({name}) at ({x},{y}) outside bounds")
            if hq_type == 0:
                hex_stacks[(player, x, y)].append(f"{uid}:{name}")
        elif delay > 0 and ax > 0 and ay > 0:
            if not in_playable_area(ax, ay, nw, se):
                off_map_units.append(f"Reinforcement {uid} ({name}) arrives at ({ax},{ay}) outside bounds")

        # 3. HQ 指挥链校验
        if hhq == "0":
            if hq_type != 1:
                warnings.append(f"[HQ] Unit {uid} ({name}, hq_type={hq_type}) has hhq=0")
        elif hhq not in alive_ids:
            bad_hq_links.append(f"Unit {uid} ({name}) -> dead/missing hhq={hhq}")
        else:
            parent = unit_by_id[hhq]
            if _to_int(parent.get("player")) != player:
                bad_hq_links.append(f"Unit {uid} ({name}, p={player}) -> cross-side hhq={hhq} (p={parent.get('player')})")
            if _to_int(parent.get("hq")) == 0:
                warnings.append(f"[HQ] Unit {uid} ({name}) -> parent hhq={hhq} ({parent.get('name')}) has hq_type=0")

    overstacks = [
        f"Player {p} hex ({hx},{hy}) has {len(members)} combat units: {members}"
        for (p, hx, hy), members in sorted(hex_stacks.items())
        if len(members) > 3
    ]

    errors.extend(f"[Off-Map] {m}" for m in off_map_units)
    errors.extend(f"[Bad HQ] {m}" for m in bad_hq_links)
    for msg in overstacks:
        warnings.append(f"[Overstack] {msg}")

    # 5. 航空队基地链接校验
    alive_airgroups = [r for r in a_rows if is_airgroup_slot_alive(r)]
    bad_airbases: list[str] = []
    for ag in alive_airgroups:
        aid = ag["id"]
        aname = ag.get("name", "")
        base = str(_to_int(ag.get("base")))
        start_base = str(_to_int(ag.get("startBase")))
        target_base = base if base != "0" else start_base
        if target_base == "0":
            warnings.append(f"[AirBase] Airgroup {aid} ({aname}) has base=0 and startBase=0")
        elif target_base not in alive_ids:
            bad_airbases.append(f"Airgroup {aid} ({aname}) -> missing/cleared base={target_base}")
        else:
            bunit = unit_by_id[target_base]
            if _to_int(bunit.get("hq")) != 5:
                warnings.append(f"[AirBase] Airgroup {aid} ({aname}) -> unit {target_base} has hq={bunit.get('hq')} (expected 5)")
    errors.extend(f"[AirBase] {m}" for m in bad_airbases)

    # 6. Husky shape2 几何校验
    husky_errors: list[str] = []
    if "husky_validation" in config:
        husky_errors = validate_husky_geometry(config["husky_validation"])
        errors.extend(f"[Husky shape2] {m}" for m in husky_errors)

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {
        "status": status,
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
    parser.add_argument("--prefix", required=True, help="剧本文件名前缀")
    parser.add_argument("--config", required=True, type=Path, help="剧本裁剪配置 JSON")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    result = validate_scenario_csvs(args.input_dir, args.prefix, config)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
