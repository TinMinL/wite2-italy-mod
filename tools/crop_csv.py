#!/usr/bin/env python3
"""WitE2 CSV 剧本裁剪工具（用于从 WITW+WITE v0.9.60 导出的 CSV 裁剪出纯意大利大/小剧本）。

设计铁律：
1. 绝不删除任何 CSV 行（保持 id 槽位与索引 1:1 不漂移）。
2. 框外无关单位安全置空（保留 id，其余置零、name=""、delay=998）。
3. 保护所有保留单位的 hhq 指挥链闭包；若祖先 HQ 原位置在框外，支持自动迁入高司锚点
   (--relocate-offmap-hqs) 或在报告中标为 RELOCATE_REQUIRED。
4. 框外城市保留行号与坐标，清零工厂、库存、补给堆、人力征募与机场绑定以减负。
5. 航空队仅保留其 base / startBase 属于框内保留机场且处于活动/有效延迟的条目。
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

from hex_geometry import in_playable_area

INACTIVE_DELAYS = {250, 998, 999}


def _to_int(val: str | None, default: int = 0) -> int:
    if val is None or val == "":
        return default
    try:
        return int(val)
    except ValueError:
        return default


def is_unit_slot_alive(row: dict[str, str]) -> bool:
    """判定 unit.csv 槽位是否为有效非空单位（排除空槽与 *** 标题行与 delay=250/998/999 停用槽）。"""
    name = (row.get("name") or "").strip()
    if not name or name.startswith("*"):
        return False
    delay = _to_int(row.get("delay"), 998)
    if delay in INACTIVE_DELAYS:
        return False
    return True


def is_airgroup_slot_alive(row: dict[str, str]) -> bool:
    """判定 airgroup.csv 槽位是否为有效航空队。"""
    name = (row.get("name") or "").strip()
    if not name or name.startswith("*"):
        return False
    delay = _to_int(row.get("delay"), 250)
    if delay in INACTIVE_DELAYS:
        return False
    return True


def clear_unit_row(row: dict[str, str], fieldnames: list[str]) -> None:
    """将 unit.csv 指定槽位安全置空为 WitE2 标准空槽（保留 id，delay=998）。"""
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


def clear_airgroup_row(row: dict[str, str], fieldnames: list[str]) -> None:
    """将 airgroup.csv 指定槽位安全置空（保留 id，delay=250）。"""
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


def strip_offmap_city_economy(row: dict[str, str]) -> bool:
    """清空框外城市的工厂、库存、港口/机场绑定与补给堆以给引擎减负，保留城市 id/name/x/y。"""
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


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, rows


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def crop_scenario_csvs(
    input_dir: Path,
    prefix: str,
    config: dict[str, Any],
    output_dir: Path,
    dry_run: bool = False,
    relocate_offmap_hqs: bool = False,
    clear_tb_locks: bool = True,
) -> dict[str, Any]:
    """执行核心 CSV 裁剪并返回审计统计字典。"""
    nw = config["map_nw_limit"]
    se = config["map_se_limit"]
    anchors = config.get("high_command_anchor", {})

    unit_path = input_dir / f"{prefix}_unit.csv"
    air_path = input_dir / f"{prefix}_airgroup.csv"
    city_path = input_dir / f"{prefix}_city.csv"

    for req in (unit_path, air_path, city_path):
        if not req.exists():
            raise FileNotFoundError(f"缺少必需 CSV 文件: {req}")

    unit_fields, unit_rows = read_csv_rows(unit_path)
    air_fields, air_rows = read_csv_rows(air_path)
    city_fields, city_rows = read_csv_rows(city_path)

    unit_by_id: dict[str, dict[str, str]] = {r["id"]: r for r in unit_rows if r.get("id")}

    # 1. 初筛直接位于可玩区内的 unit（地图单位 或 到达坐标在框内的未来增援）
    keep_ids: set[str] = set()
    direct_in_box_ids: set[str] = set()
    for row in unit_rows:
        if not is_unit_slot_alive(row):
            continue
        x, y = _to_int(row.get("x")), _to_int(row.get("y"))
        ax, ay = _to_int(row.get("ax")), _to_int(row.get("ay"))
        delay = _to_int(row.get("delay"))
        if x > 0 and y > 0 and in_playable_area(x, y, nw, se):
            keep_ids.add(row["id"])
            direct_in_box_ids.add(row["id"])
        elif delay > 0 and ax > 0 and ay > 0 and in_playable_area(ax, ay, nw, se):
            keep_ids.add(row["id"])
            direct_in_box_ids.add(row["id"])

    # 2. 向下传播保留附属在框内单位（如支援单位、在岗防空/炮兵团）上的子单位 (x==0, y==0, delay==0)
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

    # 3. 向上闭包保留祖先 HQ（防止 Bad HQ Errors），并记录框外需要迁移的高司 HQ
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
            delay = _to_int(cur.get("delay"))
            if cur_id not in direct_in_box_ids and x > 0 and y > 0 and not in_playable_area(x, y, nw, se):
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
            elif delay == 0 and x == 0 and y == 0 and _to_int(cur.get("hq")) > 0 and cur_id not in relocate_seen:
                # 无坐标的战区级 HQ（例如从 TB 拉出的司令部）
                pass
            next_hhq = str(_to_int(cur.get("hhq")))
            if next_hhq == cur_id or next_hhq == "0":
                break
            cur_id = next_hhq

    # 4. 清理框外 unit，并检查保留单位上的 TB 锁或越界撤离计划
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
            clear_unit_row(row, unit_fields)

    # 5. 裁剪 airgroup.csv：仅保留基地属于 kept_airbase_ids（或框内机场）的航空队
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
            clear_airgroup_row(row, air_fields)

    # 6. 减负 city.csv：框外城市清空工业/补给/港口/机场引用，保留行号与坐标
    cities_in_box = 0
    cities_stripped = 0
    ports_in_box: list[dict[str, Any]] = []
    for row in city_rows:
        name = (row.get("name") or "").strip()
        if not name or name.startswith("*"):
            continue
        x, y = _to_int(row.get("x")), _to_int(row.get("y"))
        if x > 0 and y > 0 and in_playable_area(x, y, nw, se):
            cities_in_box += 1
            pv = _to_int(row.get("portValue"))
            if pv > 0:
                ports_in_box.append({"id": row["id"], "name": name, "xy": [x, y], "portValue": pv})
        else:
            if strip_offmap_city_economy(row):
                cities_stripped += 1

    # 7. 写出裁剪后 CSV 与透传其余 *_*.csv 文件
    if not dry_run:
        write_csv_rows(output_dir / f"{prefix}_unit.csv", unit_fields, unit_rows)
        write_csv_rows(output_dir / f"{prefix}_airgroup.csv", air_fields, air_rows)
        write_csv_rows(output_dir / f"{prefix}_city.csv", city_fields, city_rows)
        handled = {f"{prefix}_unit.csv", f"{prefix}_airgroup.csv", f"{prefix}_city.csv"}
        for extra in input_dir.glob(f"{prefix}_*.csv"):
            if extra.name not in handled:
                shutil.copy2(extra, output_dir / extra.name)

    report = {
        "scenario_id": config.get("scenario_id"),
        "prefix": prefix,
        "dry_run": dry_run,
        "playable_nw": nw,
        "playable_se": se,
        "units_kept": units_kept,
        "units_cleared": units_cleared,
        "kept_airbases": len(kept_airbase_ids),
        "airgroups_kept": air_kept,
        "airgroups_cleared": air_cleared,
        "cities_in_box": cities_in_box,
        "cities_economy_stripped": cities_stripped,
        "ports_in_box_count": len(ports_in_box),
        "tb_locks_cleared": tb_locks_cleared,
        "relocate_offmap_hqs_applied": relocate_offmap_hqs,
        "hq_relocate_required": relocate_required,
        "withdraw_warnings_count": len(withdraw_warnings),
        "withdraw_warnings_sample": withdraw_warnings[:20],
    }
    return report


def format_report_md(report: dict[str, Any]) -> str:
    lines = [
        f"# CSV 裁剪审计报告 — `{report['scenario_id']}`",
        "",
        f"- **剧本前缀**：`{report['prefix']}`",
        f"- **Dry Run**：`{report['dry_run']}`",
        f"- **有效坐标盒**：`NW={report['playable_nw']}`, `SE={report['playable_se']}`",
        "",
        "## 实体裁剪统计",
        f"- **保留单位 (`unit.csv`)**：`{report['units_kept']}`（含机场 `{report['kept_airbases']}`）",
        f"- **置空框外单位**：`{report['units_cleared']}`",
        f"- **保留航空队 (`airgroup.csv`)**：`{report['airgroups_kept']}`",
        f"- **置空框外航空队**：`{report['airgroups_cleared']}`",
        f"- **框内城市 (`city.csv`)**：`{report['cities_in_box']}`（其中港口 `{report['ports_in_box_count']}` 座）",
        f"- **已清零经济/补给的框外城市**：`{report['cities_economy_stripped']}`",
        f"- **清理残留 TB / Lock 字段**：`{report['tb_locks_cleared']}`",
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

    ww = report.get("withdraw_warnings_sample", [])
    lines.extend(["", f"## 保留单位撤离/战区转移提醒（共 {report['withdraw_warnings_count']} 条）"])
    if ww:
        for w in ww:
            lines.append(f"- Unit `{w['id']}` ({w['name']}) slot {w['slot']}: turn={w['turn']}, dest={w['dest']}")
    else:
        lines.append("- 无待核对的撤离转移。")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="WitE2 纯意大利剧本 CSV 裁剪工具")
    parser.add_argument("--input-dir", required=True, type=Path, help="WitE2 Editor 导出的 CSV 目录")
    parser.add_argument("--prefix", required=True, help="导出的剧本文件名前缀")
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
