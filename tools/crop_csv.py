#!/usr/bin/env python3
"""WitE2 CSV 剧本裁剪工具（同时兼容 New Editor 20 文件子目录与 Old Editor 前缀格式）。

设计铁律：
1. 绝不删除任何 CSV 行（保持 ID 槽位与索引 1:1 不漂移）。
2. 编码保真：自动识别 utf-8-sig / utf-8 / latin-1（WitE2 Pilots.csv 含 ISO-8859-1 字符），原样写回。
3. New Editor 模式下：
   - 机场 (HQ=5) 在 Units.csv 中 X=0,Y=0，必须通过 Locations.csv 的 AbUnit 反查真实地图坐标。
   - 停用框外单位时保留 ID/Name，设 X=0,Y=0,ArriveX=0,ArriveY=0,Delay=250,TheaterBox=0。
   - GameEvents.csv 带有变长 <cnd>/<actSet> 尾列，按列表流式读写，只改 evActive 列。
   - 其余 16 个文件原字节无损透传复制。
4. 保护所有保留单位的指挥链闭包；框外祖先 HQ 可通过 --relocate-offmap-hqs 迁入锚点。
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from hex_geometry import is_hex_included

INACTIVE_DELAYS = {250, 998, 999}


def _to_int(val: str | None, default: int = 0) -> int:
    if val is None or val == "":
        return default
    try:
        return int(val)
    except ValueError:
        return default


def detect_csv_encoding(path: Path) -> str:
    """检测 CSV 文件编码，优先保留 BOM 与 Latin-1 兼容。"""
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"


def detect_editor_layout(input_dir: Path, prefix: str = "") -> str:
    """判断输入目录是 New Editor 子目录格式 ('new') 还是 Old Editor 前缀格式 ('old')。"""
    if (input_dir / "Units.csv").exists() and (input_dir / "Locations.csv").exists():
        return "new"
    if prefix and (input_dir / f"{prefix}_unit.csv").exists():
        return "old"
    raise FileNotFoundError(
        f"未在 {input_dir} 找到 New Editor (Units.csv) 或 Old Editor ({prefix}_unit.csv) 文件"
    )


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]], str]:
    enc = detect_csv_encoding(path)
    with path.open("r", encoding=enc, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, rows, enc


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]], encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def is_unit_slot_alive(row: dict[str, str]) -> bool:
    name = (row.get("name") or row.get("Name") or "").strip()
    if not name or name.startswith("*"):
        return False
    delay = _to_int(row.get("delay") if "delay" in row else row.get("Delay"), 998)
    return delay not in INACTIVE_DELAYS


def is_airgroup_slot_alive(row: dict[str, str]) -> bool:
    name = (row.get("name") or row.get("Name") or "").strip()
    if not name or name.startswith("*"):
        return False
    delay = _to_int(row.get("delay") if "delay" in row else row.get("Delay"), 250)
    return delay not in INACTIVE_DELAYS


# ---------- Old Editor 清理辅助 ----------

def clear_old_unit_row(row: dict[str, str], fieldnames: list[str]) -> None:
    uid = row["id"]
    for col in fieldnames:
        if col == "id":
            row[col] = uid
        elif col == "name":
            row[col] = ""
        elif col == "delay":
            row[col] = "998"
        else:
            row[col] = "0"


def clear_old_airgroup_row(row: dict[str, str], fieldnames: list[str]) -> None:
    aid = row["id"]
    for col in fieldnames:
        if col == "id":
            row[col] = aid
        elif col == "name":
            row[col] = ""
        elif col == "delay":
            row[col] = "250"
        else:
            row[col] = "0"


def strip_old_city_economy(row: dict[str, str]) -> bool:
    changed = False
    zero_cols = [
        "capacity", "cityDamage", "comDamage", "factoryValue",
        "oilStore", "fuelStore", "railValue", "portValue",
        "supplyStore", "supplyReq", "resourceReq", "fuelReq", "oilReq",
        "recruits", "pop", "oil", "resourceStore", "resource",
        "abUnit", "abSize", "abDamage", "supplyDumpNum", "supplyReqProd",
        "temporaryPort", "freight", "trucks", "trucksUsed", "railPoints",
        "depot", "freightSource", "portPoints", "tempPortHq", "freightLost",
        "priority", "abBuildPct", "temporaryDepot", "freightTurn",
    ]
    for i in range(20):
        zero_cols.extend([f"factory {i}", f"fNum {i}", f"damage {i}", f"delay {i}", f"repair {i}"])
    for col in zero_cols:
        if col in row and row[col] != "0":
            row[col] = "0"
            changed = True
    return changed


# ---------- New Editor 清理辅助 ----------

def deactivate_new_unit_row(row: dict[str, str]) -> None:
    """New Editor 规范：保留 ID 与 Name，清除位置与兵力/补给，设 Delay=250 停用。"""
    for col in ("X", "Y", "ArriveX", "ArriveY", "TheaterBox", "Frozen", "Reserve", "Men", "Supply", "Ammo", "Fuel"):
        if col in row:
            row[col] = "0"
    row["Delay"] = "250"


def deactivate_new_airgroup_row(row: dict[str, str]) -> None:
    """New Editor 规范：保留 ID 与 Name，断开 Base，设 Delay=250 停用。"""
    for col in ("Base", "StartBase", "TheaterBox", "ThBoxLock"):
        if col in row:
            row[col] = "0"
    row["Delay"] = "250"


def strip_new_location_economy(row: dict[str, str]) -> bool:
    changed = False
    zero_cols = [
        "Pop", "Capacity", "CityDamage", "ComDamage", "FactoryValue",
        "Depot", "RailValue", "PortValue", "Oil", "OilStore", "FuelStore",
        "SupplyStore", "Resource", "ResourceStore", "Freight",
        "AbUnit", "AbSize", "AbDamage", "Priority",
    ]
    for i in range(1, 21):
        zero_cols.extend([
            f"Factory{i}", f"FacQty{i}", f"FacDamage{i}", f"FacRepair{i}", f"FacDelay{i}"
        ])
    for col in zero_cols:
        if col in row and row[col] != "0":
            row[col] = "0"
            changed = True
    return changed


def crop_new_events_csv(
    events_path: Path,
    out_path: Path,
    events_policy: dict[str, Any],
    dry_run: bool,
) -> dict[str, Any]:
    """按列表流式裁剪 GameEvents.csv，完整保留变长 <cnd>/<actSet> 尾列。"""
    enc = detect_csv_encoding(events_path)
    with events_path.open("r", encoding=enc, newline="") as f:
        rows = list(csv.reader(f))

    if not rows:
        return {"events_kept_active": 0, "events_disabled": 0, "disabled_samples": []}

    hdr = rows[0]
    active_idx = hdr.index("evActive") if "evActive" in hdr else 12
    disable_ids = {str(x) for x in events_policy.get("disable_event_ids", [])}
    disable_kws = [str(k).lower() for k in events_policy.get("disable_title_keywords", [])]
    if events_policy.get("disable_italian_armistice") and "italy surrenders" not in disable_kws:
        disable_kws.append("italy surrenders")

    kept_active = 0
    disabled_count = 0
    disabled_samples: list[dict[str, str]] = []

    for row in rows[1:]:
        if len(row) <= active_idx:
            continue
        eid = row[0].strip()
        title = row[1].strip()
        was_active = row[active_idx].strip() == "1"
        if not was_active:
            continue
        title_low = title.lower()
        should_disable = (eid in disable_ids) or any(kw in title_low for kw in disable_kws)
        if should_disable:
            row[active_idx] = "0"
            disabled_count += 1
            disabled_samples.append({"id": eid, "title": title})
        else:
            kept_active += 1

    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding=enc, newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    return {
        "events_kept_active": kept_active,
        "events_disabled": disabled_count,
        "disabled_samples": disabled_samples,
    }


def _crop_new_editor(
    input_dir: Path,
    config: dict[str, Any],
    output_dir: Path,
    dry_run: bool,
    relocate_offmap_hqs: bool,
    clear_tb_locks: bool,
) -> dict[str, Any]:
    nw = config["map_nw_limit"]
    se = config["map_se_limit"]
    exclude_boxes = config.get("exclude_boxes", [])
    anchors = config.get("high_command_anchor", {})

    unit_fields, unit_rows, unit_enc = read_csv_rows(input_dir / "Units.csv")
    air_fields, air_rows, air_enc = read_csv_rows(input_dir / "AirGroups.csv")
    loc_fields, loc_rows, loc_enc = read_csv_rows(input_dir / "Locations.csv")

    unit_by_id: dict[str, dict[str, str]] = {r["ID"]: r for r in unit_rows if r.get("ID")}

    # 1. 先扫描 Locations.csv 获取有效区域内的机场 AbUnit -> (X, Y)
    kept_airbase_xy: dict[str, tuple[int, int]] = {}
    cities_in_box = 0
    cities_stripped = 0
    ports_in_box: list[dict[str, Any]] = []

    for row in loc_rows:
        name = (row.get("Name") or "").strip()
        if not name or name.startswith("*"):
            continue
        x, y = _to_int(row.get("X")), _to_int(row.get("Y"))
        if x > 0 and y > 0 and is_hex_included(x, y, nw, se, exclude_boxes):
            cities_in_box += 1
            ab_id = str(_to_int(row.get("AbUnit")))
            if ab_id != "0":
                kept_airbase_xy[ab_id] = (x, y)
            pv = _to_int(row.get("PortValue"))
            if pv > 0:
                ports_in_box.append({"id": row["ID"], "name": name, "xy": [x, y], "portValue": pv})
        else:
            if strip_new_location_economy(row):
                cities_stripped += 1

    # 2. 初筛 Units.csv：地图单位 + 框内延迟增援 + 框内机场 (AbUnit)
    keep_ids: set[str] = set()
    direct_in_box_ids: set[str] = set()

    for row in unit_rows:
        if not is_unit_slot_alive(row):
            continue
        uid = row["ID"]
        x, y = _to_int(row.get("X")), _to_int(row.get("Y"))
        ax, ay = _to_int(row.get("ArriveX")), _to_int(row.get("ArriveY"))
        delay = _to_int(row.get("Delay"))
        if uid in kept_airbase_xy:
            keep_ids.add(uid)
            direct_in_box_ids.add(uid)
        elif x > 0 and y > 0 and is_hex_included(x, y, nw, se, exclude_boxes):
            keep_ids.add(uid)
            direct_in_box_ids.add(uid)
        elif delay > 0 and ax > 0 and ay > 0 and is_hex_included(ax, ay, nw, se, exclude_boxes):
            keep_ids.add(uid)
            direct_in_box_ids.add(uid)

    # 2b. 处理声明式历史豁免白名单 (force_keep_units)
    force_keep_applied: list[dict[str, Any]] = []
    for spec in config.get("force_keep_units", []):
        uid = str(spec["id"])
        row = unit_by_id.get(uid)
        if not row or not is_unit_slot_alive(row):
            continue
        keep_ids.add(uid)
        direct_in_box_ids.add(uid)
        field_map = {
            "x": "X",
            "y": "Y",
            "arrive_x": "ArriveX",
            "arrive_y": "ArriveY",
            "delay": "Delay",
            "frozen": "Frozen",
            "morale": "Morale",
            "higher_hq": "HigherHQ",
            "theater_box": "TheaterBox",
        }
        applied_fields: dict[str, Any] = {}
        for cfg_key, csv_col in field_map.items():
            if cfg_key in spec and csv_col in row:
                row[csv_col] = str(spec[cfg_key])
                applied_fields[csv_col] = row[csv_col]
        force_keep_applied.append({
            "id": uid,
            "name": row.get("Name", ""),
            "note": spec.get("name_note", ""),
            "applied": applied_fields,
        })

    # 3. 向下传播挂载在保留单位上的支援单位 (X==0, Y==0, Delay==0, HQ!=5)
    changed = True
    while changed:
        changed = False
        for row in unit_rows:
            uid = row["ID"]
            if uid in keep_ids or not is_unit_slot_alive(row):
                continue
            x, y = _to_int(row.get("X")), _to_int(row.get("Y"))
            delay = _to_int(row.get("Delay"))
            hq_type = _to_int(row.get("HQ"))
            hhq = str(_to_int(row.get("HigherHQ")))
            if x == 0 and y == 0 and delay == 0 and hq_type != 5 and hhq in keep_ids:
                keep_ids.add(uid)
                changed = True

    # 4. 向上闭包保留祖先 HigherHQ，并记录/迁移框外 HQ
    relocate_required: list[dict[str, Any]] = []
    relocate_seen: set[str] = set()
    for uid in list(keep_ids):
        cur_id = uid
        visited: set[str] = set()
        while cur_id and cur_id != "0" and cur_id not in visited:
            visited.add(cur_id)
            cur = unit_by_id.get(cur_id)
            if not cur:
                break
            keep_ids.add(cur_id)
            x, y = _to_int(cur.get("X")), _to_int(cur.get("Y"))
            ax, ay = _to_int(cur.get("ArriveX")), _to_int(cur.get("ArriveY"))
            delay = _to_int(cur.get("Delay"))
            offmap_pos = x > 0 and y > 0 and not is_hex_included(x, y, nw, se, exclude_boxes)
            offmap_arr = delay > 0 and ax > 0 and ay > 0 and not is_hex_included(ax, ay, nw, se, exclude_boxes)
            if cur_id not in direct_in_box_ids and (offmap_pos or offmap_arr):
                if cur_id not in relocate_seen:
                    relocate_seen.add(cur_id)
                    player = _to_int(cur.get("Player"))
                    side = "axis" if player == 1 else "allied"
                    anchor_xy = anchors.get(side, {}).get("xy")
                    relocate_required.append({
                        "id": cur_id,
                        "name": cur.get("Name", ""),
                        "player": player,
                        "old_xy": [x, y] if offmap_pos else [ax, ay],
                        "suggested_anchor_xy": anchor_xy,
                    })
                    if relocate_offmap_hqs and anchor_xy and len(anchor_xy) == 2:
                        if offmap_pos:
                            cur["X"] = str(anchor_xy[0])
                            cur["Y"] = str(anchor_xy[1])
                        if offmap_arr:
                            cur["ArriveX"] = str(anchor_xy[0])
                            cur["ArriveY"] = str(anchor_xy[1])
            next_hhq = str(_to_int(cur.get("HigherHQ")))
            if next_hhq == cur_id or next_hhq == "0":
                break
            cur_id = next_hhq

    # 5. 停用框外 Units，清理保留单位上的 TheaterBox 锁，应用历史冻结与士气校准
    units_kept = 0
    units_cleared = 0
    tb_locks_cleared = 0
    kept_airbase_ids: set[str] = set()
    withdraw_warnings: list[dict[str, Any]] = []

    freeze_cfg = config.get("freeze_unit_ids", {})
    freeze_turns = _to_int(freeze_cfg.get("turns"), 0)
    freeze_set = {str(x) for x in freeze_cfg.get("unit_ids", [])}
    frozen_applied: list[dict[str, Any]] = []

    morale_map = {str(k): int(v) for k, v in config.get("morale_overrides", {}).items()}
    morale_applied: list[dict[str, Any]] = []

    for row in unit_rows:
        uid = row["ID"]
        if uid in keep_ids and is_unit_slot_alive(row):
            units_kept += 1
            if _to_int(row.get("HQ")) == 5:
                kept_airbase_ids.add(uid)
            if clear_tb_locks and _to_int(row.get("TheaterBox")) != 0:
                row["TheaterBox"] = "0"
                tb_locks_cleared += 1
            if uid in freeze_set and freeze_turns > 0:
                old_frz = _to_int(row.get("Frozen"))
                if old_frz < freeze_turns:
                    row["Frozen"] = str(freeze_turns)
                    frozen_applied.append({"id": uid, "name": row.get("Name", ""), "old": old_frz, "new": freeze_turns})
            if uid in morale_map:
                old_mor = _to_int(row.get("Morale"))
                row["Morale"] = str(morale_map[uid])
                morale_applied.append({"id": uid, "name": row.get("Name", ""), "old": old_mor, "new": morale_map[uid]})
            wt = _to_int(row.get("WithdrawTurn"))
            if wt > 0:
                withdraw_warnings.append({
                    "id": uid,
                    "name": row.get("Name"),
                    "turn": wt,
                    "state": _to_int(row.get("WithdrawState")),
                })
        elif is_unit_slot_alive(row):
            units_cleared += 1
            deactivate_new_unit_row(row)

    # 6. 裁剪 AirGroups.csv
    air_kept = 0
    air_cleared = 0
    for row in air_rows:
        if not is_airgroup_slot_alive(row):
            continue
        base = str(_to_int(row.get("Base")))
        start_base = str(_to_int(row.get("StartBase")))
        if base in kept_airbase_ids or (base == "0" and start_base in kept_airbase_ids):
            air_kept += 1
            if clear_tb_locks:
                if _to_int(row.get("TheaterBox")) != 0:
                    row["TheaterBox"] = "0"
                    tb_locks_cleared += 1
                if _to_int(row.get("ThBoxLock")) != 0:
                    row["ThBoxLock"] = "0"
                    tb_locks_cleared += 1
        else:
            air_cleared += 1
            deactivate_new_airgroup_row(row)

    # 7. 裁剪 GameEvents.csv
    events_path = input_dir / "GameEvents.csv"
    events_stats = {"events_kept_active": 0, "events_disabled": 0, "disabled_samples": []}
    if events_path.exists():
        events_stats = crop_new_events_csv(
            events_path=events_path,
            out_path=output_dir / "GameEvents.csv",
            events_policy=config.get("events_policy", {}),
            dry_run=dry_run,
        )

    # 8. 写出核心文件并原字节透传其余 CSV
    if not dry_run:
        write_csv_rows(output_dir / "Units.csv", unit_fields, unit_rows, encoding=unit_enc)
        write_csv_rows(output_dir / "AirGroups.csv", air_fields, air_rows, encoding=air_enc)
        write_csv_rows(output_dir / "Locations.csv", loc_fields, loc_rows, encoding=loc_enc)
        handled = {"Units.csv", "AirGroups.csv", "Locations.csv", "GameEvents.csv"}
        for extra in input_dir.glob("*.csv"):
            if extra.name not in handled:
                shutil.copy2(extra, output_dir / extra.name)

    return {
        "editor_layout": "new",
        "scenario_id": config.get("scenario_id"),
        "prefix": input_dir.name,
        "dry_run": dry_run,
        "playable_nw": nw,
        "playable_se": se,
        "exclude_boxes_count": len(exclude_boxes),
        "units_kept": units_kept,
        "units_cleared": units_cleared,
        "kept_airbases": len(kept_airbase_ids),
        "airgroups_kept": air_kept,
        "airgroups_cleared": air_cleared,
        "cities_in_box": cities_in_box,
        "cities_economy_stripped": cities_stripped,
        "ports_in_box_count": len(ports_in_box),
        "tb_locks_cleared": tb_locks_cleared,
        "events_kept_active": events_stats["events_kept_active"],
        "events_disabled": events_stats["events_disabled"],
        "events_disabled_samples": events_stats["disabled_samples"],
        "relocate_offmap_hqs_applied": relocate_offmap_hqs,
        "hq_relocate_required": relocate_required,
        "force_keep_applied": force_keep_applied,
        "frozen_by_policy": frozen_applied,
        "morale_overrides_applied": morale_applied,
        "withdraw_warnings_count": len(withdraw_warnings),
        "withdraw_warnings_sample": withdraw_warnings[:20],
    }


def _crop_old_editor(
    input_dir: Path,
    prefix: str,
    config: dict[str, Any],
    output_dir: Path,
    dry_run: bool,
    relocate_offmap_hqs: bool,
    clear_tb_locks: bool,
) -> dict[str, Any]:
    nw = config["map_nw_limit"]
    se = config["map_se_limit"]
    exclude_boxes = config.get("exclude_boxes", [])
    anchors = config.get("high_command_anchor", {})

    unit_fields, unit_rows, unit_enc = read_csv_rows(input_dir / f"{prefix}_unit.csv")
    air_fields, air_rows, air_enc = read_csv_rows(input_dir / f"{prefix}_airgroup.csv")
    city_fields, city_rows, city_enc = read_csv_rows(input_dir / f"{prefix}_city.csv")

    unit_by_id: dict[str, dict[str, str]] = {r["id"]: r for r in unit_rows if r.get("id")}

    keep_ids: set[str] = set()
    direct_in_box_ids: set[str] = set()
    for row in unit_rows:
        if not is_unit_slot_alive(row):
            continue
        x, y = _to_int(row.get("x")), _to_int(row.get("y"))
        ax, ay = _to_int(row.get("ax")), _to_int(row.get("ay"))
        delay = _to_int(row.get("delay"))
        if x > 0 and y > 0 and is_hex_included(x, y, nw, se, exclude_boxes):
            keep_ids.add(row["id"])
            direct_in_box_ids.add(row["id"])
        elif delay > 0 and ax > 0 and ay > 0 and is_hex_included(ax, ay, nw, se, exclude_boxes):
            keep_ids.add(row["id"])
            direct_in_box_ids.add(row["id"])

    changed = True
    while changed:
        changed = False
        for row in unit_rows:
            uid = row["id"]
            if uid in keep_ids or not is_unit_slot_alive(row):
                continue
            x, y = _to_int(row.get("x")), _to_int(row.get("y"))
            delay = _to_int(row.get("delay"))
            hhq = str(_to_int(row.get("hhq")))
            if x == 0 and y == 0 and delay == 0 and hhq in keep_ids:
                keep_ids.add(uid)
                changed = True

    relocate_required: list[dict[str, Any]] = []
    relocate_seen: set[str] = set()
    for uid in list(keep_ids):
        cur_id = uid
        visited: set[str] = set()
        while cur_id and cur_id != "0" and cur_id not in visited:
            visited.add(cur_id)
            cur = unit_by_id.get(cur_id)
            if not cur:
                break
            keep_ids.add(cur_id)
            x, y = _to_int(cur.get("x")), _to_int(cur.get("y"))
            if cur_id not in direct_in_box_ids and x > 0 and y > 0 and not is_hex_included(x, y, nw, se, exclude_boxes):
                if cur_id not in relocate_seen:
                    relocate_seen.add(cur_id)
                    player = _to_int(cur.get("player"))
                    side = "axis" if player == 1 else "allied"
                    anchor_xy = anchors.get(side, {}).get("xy")
                    relocate_required.append({
                        "id": cur_id,
                        "name": cur.get("name", ""),
                        "player": player,
                        "old_xy": [x, y],
                        "suggested_anchor_xy": anchor_xy,
                    })
                    if relocate_offmap_hqs and anchor_xy and len(anchor_xy) == 2:
                        cur["x"] = str(anchor_xy[0])
                        cur["y"] = str(anchor_xy[1])
            next_hhq = str(_to_int(cur.get("hhq")))
            if next_hhq == cur_id or next_hhq == "0":
                break
            cur_id = next_hhq

    units_kept = 0
    units_cleared = 0
    tb_locks_cleared = 0
    withdraw_warnings: list[dict[str, Any]] = []
    kept_airbase_ids: set[str] = set()

    for row in unit_rows:
        uid = row["id"]
        if uid in keep_ids and is_unit_slot_alive(row):
            units_kept += 1
            if _to_int(row.get("hq")) == 5:
                kept_airbase_ids.add(uid)
            if clear_tb_locks:
                if _to_int(row.get("theaterBox")) != 0:
                    row["theaterBox"] = "0"
                    tb_locks_cleared += 1
                if _to_int(row.get("thBoxLock")) != 0:
                    row["thBoxLock"] = "0"
                    tb_locks_cleared += 1
            for wi in range(5):
                wt = _to_int(row.get(f"withTurn {wi}"))
                wd = _to_int(row.get(f"withDest {wi}"))
                if wt > 0 and wd != 0:
                    withdraw_warnings.append({"id": uid, "name": row.get("name"), "slot": wi, "turn": wt, "dest": wd})
        elif is_unit_slot_alive(row):
            units_cleared += 1
            clear_old_unit_row(row, unit_fields)

    air_kept = 0
    air_cleared = 0
    for row in air_rows:
        if not is_airgroup_slot_alive(row):
            continue
        base = str(_to_int(row.get("base")))
        start_base = str(_to_int(row.get("startBase")))
        if base in kept_airbase_ids or (base == "0" and start_base in kept_airbase_ids):
            air_kept += 1
        else:
            air_cleared += 1
            clear_old_airgroup_row(row, air_fields)

    cities_in_box = 0
    cities_stripped = 0
    ports_in_box: list[dict[str, Any]] = []
    for row in city_rows:
        name = (row.get("name") or "").strip()
        if not name or name.startswith("*"):
            continue
        x, y = _to_int(row.get("x")), _to_int(row.get("y"))
        if x > 0 and y > 0 and is_hex_included(x, y, nw, se, exclude_boxes):
            cities_in_box += 1
            pv = _to_int(row.get("portValue"))
            if pv > 0:
                ports_in_box.append({"id": row["id"], "name": name, "xy": [x, y], "portValue": pv})
        else:
            if strip_old_city_economy(row):
                cities_stripped += 1

    if not dry_run:
        write_csv_rows(output_dir / f"{prefix}_unit.csv", unit_fields, unit_rows, encoding=unit_enc)
        write_csv_rows(output_dir / f"{prefix}_airgroup.csv", air_fields, air_rows, encoding=air_enc)
        write_csv_rows(output_dir / f"{prefix}_city.csv", city_fields, city_rows, encoding=city_enc)
        handled = {f"{prefix}_unit.csv", f"{prefix}_airgroup.csv", f"{prefix}_city.csv"}
        for extra in input_dir.glob(f"{prefix}_*.csv"):
            if extra.name not in handled:
                shutil.copy2(extra, output_dir / extra.name)

    return {
        "editor_layout": "old",
        "scenario_id": config.get("scenario_id"),
        "prefix": prefix,
        "dry_run": dry_run,
        "playable_nw": nw,
        "playable_se": se,
        "exclude_boxes_count": len(exclude_boxes),
        "units_kept": units_kept,
        "units_cleared": units_cleared,
        "kept_airbases": len(kept_airbase_ids),
        "airgroups_kept": air_kept,
        "airgroups_cleared": air_cleared,
        "cities_in_box": cities_in_box,
        "cities_economy_stripped": cities_stripped,
        "ports_in_box_count": len(ports_in_box),
        "tb_locks_cleared": tb_locks_cleared,
        "events_kept_active": 0,
        "events_disabled": 0,
        "events_disabled_samples": [],
        "relocate_offmap_hqs_applied": relocate_offmap_hqs,
        "hq_relocate_required": relocate_required,
        "force_keep_applied": [],
        "frozen_by_policy": [],
        "morale_overrides_applied": [],
        "withdraw_warnings_count": len(withdraw_warnings),
        "withdraw_warnings_sample": withdraw_warnings[:20],
    }


def crop_scenario_csvs(
    input_dir: Path,
    prefix: str,
    config: dict[str, Any],
    output_dir: Path,
    dry_run: bool = False,
    relocate_offmap_hqs: bool = False,
    clear_tb_locks: bool = True,
) -> dict[str, Any]:
    """自动适配 New Editor / Old Editor 格式并执行裁剪。"""
    layout = detect_editor_layout(input_dir, prefix)
    if layout == "new":
        return _crop_new_editor(input_dir, config, output_dir, dry_run, relocate_offmap_hqs, clear_tb_locks)
    return _crop_old_editor(input_dir, prefix, config, output_dir, dry_run, relocate_offmap_hqs, clear_tb_locks)


def format_report_md(report: dict[str, Any]) -> str:
    lines = [
        f"# CSV 裁剪审计报告 — `{report['scenario_id']}`",
        "",
        f"- **CSV 格式**：`{report['editor_layout']}`",
        f"- **来源标识**：`{report['prefix']}`",
        f"- **Dry Run**：`{report['dry_run']}`",
        f"- **有效坐标盒**：`NW={report['playable_nw']}`, `SE={report['playable_se']}`（排除区 `{report['exclude_boxes_count']}` 个）",
        "",
        "## 实体裁剪统计",
        f"- **保留单位**：`{report['units_kept']}`（含机场 `{report['kept_airbases']}`）",
        f"- **停用/置空框外单位**：`{report['units_cleared']}`",
        f"- **保留航空队**：`{report['airgroups_kept']}`",
        f"- **停用/置空框外航空队**：`{report['airgroups_cleared']}`",
        f"- **框内城市**：`{report['cities_in_box']}`（其中港口 `{report['ports_in_box_count']}` 座）",
        f"- **已清零经济/补给的框外城市**：`{report['cities_economy_stripped']}`",
        f"- **清理残留 TB / Lock 字段**：`{report['tb_locks_cleared']}`",
        f"- **活跃事件保留 / 停用**：`{report['events_kept_active']}` / `{report['events_disabled']}`",
        "",
    ]
    hqs = report.get("hq_relocate_required", [])
    lines.append(f"## 需迁移或已自动迁移的祖先 HQ（共 {len(hqs)} 个）")
    if hqs:
        lines.append("| Unit ID | 名称 | Player | 原坐标 | 建议锚点坐标 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for h in hqs:
            lines.append(f"| {h['id']} | {h['name']} | {h['player']} | {h['old_xy']} | {h['suggested_anchor_xy']} |")
    else:
        lines.append("- 无框外祖先 HQ。")

    ev_dis = report.get("events_disabled_samples", [])
    lines.extend(["", f"## 已停用的活跃事件（共 {len(ev_dis)} 条）"])
    if ev_dis:
        for e in ev_dis[:40]:
            lines.append(f"- Event `{e['id']}`: {e['title']}")
        if len(ev_dis) > 40:
            lines.append(f"- ...（其余 {len(ev_dis) - 40} 条省略）")
    else:
        lines.append("- 无被停用的活跃事件。")

    ww = report.get("withdraw_warnings_sample", [])
    lines.extend(["", f"## 保留单位撤离/战区转移提醒（共 {report['withdraw_warnings_count']} 条）"])
    if ww:
        for w in ww:
            lines.append(f"- Unit `{w['id']}` ({w['name']}): {w}")
    else:
        lines.append("- 无待核对的撤离转移。")

    fku = report.get("force_keep_applied", [])
    lines.extend(["", f"## 历史豁免与部署覆写 (`force_keep_units`, 共 {len(fku)} 条)"])
    if fku:
        for item in fku:
            lines.append(f"- Unit `{item['id']}` ({item['name']}): {item['applied']} — {item['note']}")
    else:
        lines.append("- 无。")

    fbp = report.get("frozen_by_policy", [])
    lines.extend(["", f"## 非参战部队政策冻结 (`freeze_unit_ids`, 共 {len(fbp)} 条)"])
    if fbp:
        for item in fbp:
            lines.append(f"- Unit `{item['id']}` ({item['name']}): Frozen {item['old']} -> {item['new']}")
    else:
        lines.append("- 无。")

    mor = report.get("morale_overrides_applied", [])
    lines.extend(["", f"## 基于 WITW 史料的士气校准 (`morale_overrides`, 共 {len(mor)} 条)"])
    if mor:
        for item in mor:
            lines.append(f"- Unit `{item['id']}` ({item['name']}): Morale {item['old']} -> {item['new']}")
    else:
        lines.append("- 无。")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="WitE2 纯意大利剧本 CSV 裁剪工具")
    parser.add_argument("--input-dir", required=True, type=Path, help="WitE2 Editor 导出的 CSV 目录")
    parser.add_argument("--prefix", default="", help="Old Editor 前缀（New Editor 子目录可留空）")
    parser.add_argument("--config", required=True, type=Path, help="剧本裁剪配置 JSON")
    parser.add_argument("--output-dir", required=True, type=Path, help="裁剪后 CSV 输出目录")
    parser.add_argument("--dry-run", action="store_true", help="仅统计和输出报告，不写入 CSV 文件")
    parser.add_argument("--relocate-offmap-hqs", action="store_true", help="自动将框外祖先 HQ 迁至配置锚点")
    parser.add_argument("--report", type=Path, default=None, help="可选输出 Markdown 报告路径")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    report = crop_scenario_csvs(
        input_dir=args.input_dir,
        prefix=args.prefix,
        config=config,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        relocate_offmap_hqs=args.relocate_offmap_hqs,
    )
    md = format_report_md(report)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(md, encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
