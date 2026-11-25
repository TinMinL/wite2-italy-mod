#!/usr/bin/env python3
"""对比本地官方 WITW《哈士奇行动》CSV 与本仓库裁剪产出的 `Italy_Husky_43` CSV，生成审计对照报告。"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any

MOD_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WITW_DIR = Path(r"E:\SteamLibrary\steamapps\common\Gary Grigsbys War in the West\Dat\CSV")
DEFAULT_WITW_PREFIX = "Introductory Scenario - Operation Husky"
DEFAULT_MOD_DIR = MOD_ROOT / "output" / "Italy_Husky_43"
DEFAULT_OUT_MD = MOD_ROOT / "docs" / "WITW_HUSKY_COMPARISON.md"

INACTIVE_DELAYS = {250, 998, 999}


def _to_int(v: str | None, default: int = 0) -> int:
    if v is None or v == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


def load_witw_husky(witw_dir: Path, prefix: str) -> dict[str, Any]:
    with (witw_dir / f"{prefix}_unit.csv").open("r", encoding="latin-1", newline="") as f:
        units = list(csv.DictReader(f))
    with (witw_dir / f"{prefix}_airgroup.csv").open("r", encoding="latin-1", newline="") as f:
        ags = list(csv.DictReader(f))

    alive = [
        u for u in units
        if u["name"].strip() and not u["name"].startswith("*") and _to_int(u["delay"], 998) not in INACTIVE_DELAYS
    ]
    combat_or_hq = [
        u for u in alive
        if _to_int(u["hq"]) != 5 and (_to_int(u["x"]) > 0 or (0 < _to_int(u["delay"]) < 250))
    ]
    unfrozen_allied_divs = [
        u for u in combat_or_hq
        if u["player"] == "2" and _to_int(u["hq"]) == 0 and _to_int(u.get("frozen")) == 0 and _to_int(u["delay"]) == 0
    ]
    axis_combat = [
        u for u in combat_or_hq
        if u["player"] == "1" and _to_int(u["hq"]) == 0
    ]
    active_ags = [
        a for a in ags
        if a["name"].strip() and not a["name"].startswith("*") and _to_int(a["delay"], 250) not in INACTIVE_DELAYS
    ]
    return {
        "total_alive": len(alive),
        "combat_or_hq": combat_or_hq,
        "unfrozen_allied_divs": unfrozen_allied_divs,
        "axis_combat": axis_combat,
        "airgroups": len(active_ags),
        "airgroups_by_player": dict(Counter(a["player"] for a in active_ags)),
    }


def load_mod_husky(mod_dir: Path) -> dict[str, Any]:
    with (mod_dir / "Units.csv").open("r", encoding="utf-8-sig", newline="") as f:
        units = list(csv.DictReader(f))
    with (mod_dir / "AirGroups.csv").open("r", encoding="utf-8-sig", newline="") as f:
        ags = list(csv.DictReader(f))

    alive = [
        u for u in units
        if u["Name"].strip() and not u["Name"].startswith("*") and _to_int(u["Delay"], 998) not in INACTIVE_DELAYS
    ]
    combat_or_hq = [
        u for u in alive
        if _to_int(u["HQ"]) != 5 and (_to_int(u["X"]) > 0 or (0 < _to_int(u["Delay"]) < 250))
    ]
    unfrozen_allied_divs = [
        u for u in combat_or_hq
        if u["Player"] == "2" and _to_int(u["HQ"]) == 0 and _to_int(u.get("Frozen")) == 0 and _to_int(u["Delay"]) == 0
    ]
    frozen_allied_divs = [
        u for u in combat_or_hq
        if u["Player"] == "2" and _to_int(u["HQ"]) == 0 and _to_int(u.get("Frozen")) > 0
    ]
    axis_combat = [
        u for u in combat_or_hq
        if u["Player"] == "1" and _to_int(u["HQ"]) == 0
    ]
    active_ags = [
        a for a in ags
        if a["Name"].strip() and not a["Name"].startswith("*") and _to_int(a["Delay"], 250) not in INACTIVE_DELAYS
    ]
    return {
        "total_alive": len(alive),
        "combat_or_hq": combat_or_hq,
        "unfrozen_allied_divs": unfrozen_allied_divs,
        "frozen_allied_divs": frozen_allied_divs,
        "axis_combat": axis_combat,
        "airgroups": len(active_ags),
        "airgroups_by_player": dict(Counter(a["Player"] for a in active_ags)),
    }


def build_comparison_md(witw: dict[str, Any], mod: dict[str, Any]) -> str:
    lines = [
        "# 官方 WITW《哈士奇行动》vs `Italy_Husky_43` 历史对照报告",
        "",
        "> 由 `tools/compare_witw_husky.py` 基于本地官方 WITW CSV 与本仓库真实裁剪输出自动对比生成。",
        "",
        "## 1. 总体规模对比",
        "| 指标 | 官方 WITW *Operation Husky* | 本项目 `Italy_Husky_43` | 说明 |",
        "| --- | --- | --- | --- |",
        f"| 地图作战/HQ 单位数 | `{len(witw['combat_or_hq'])}` | `{len(mod['combat_or_hq'])}` | 本项目含北非未参战冻结师占位 |",
        f"| 开局未冻结盟军战斗师/旅 (`Frozen=0`) | `{len(witw['unfrozen_allied_divs'])}` | `{len(mod['unfrozen_allied_divs'])}` | 已将11支9月萨莱诺师冻结，仅保留历史参战部队 + 2nd SAS |",
        f"| 轴心战场/增援战斗部队 | `{len(witw['axis_combat'])}` | `{len(mod['axis_combat'])}` | 含第29装掷师(631)与第1伞兵师(2044) |",
        f"| 活跃/计划航空队数 | `{witw['airgroups']}` (`{witw['airgroups_by_player']}`) | `{mod['airgroups']}` (`{mod['airgroups_by_player']}`) | 升级至 `v0.9.65` 后轴心机场与飞行员将进一步补全 |",
        "",
        "## 2. 开局未冻结盟军参战师/旅清单对照",
        f"- **官方 WITW ({len(witw['unfrozen_allied_divs'])} 支)**：" + "、".join(
            f"{u['name']} ({u['x']},{u['y']})" for u in sorted(witw["unfrozen_allied_divs"], key=lambda r: (int(r["x"]), r["name"]))
        ),
        f"- **本项目 ({len(mod['unfrozen_allied_divs'])} 支)**：" + "、".join(
            f"{u['Name']} ({u['X']},{u['Y']})" for u in sorted(mod["unfrozen_allied_divs"], key=lambda r: (int(r["X"]), r["Name"]))
        ),
        f"- **本项目已冻结的非西西里北非师 ({len(mod['frozen_allied_divs'])} 支)**：含 11 支萨莱诺/半岛师（`Frozen=12`）与原版长冻结预备师。",
        "",
        "## 3. 核心轴心参战师士气与部署校准对照",
        "| 部队 | 官方 WITW 坐标 / 延迟 / 士气 | 本项目校准后坐标 / 延迟 / 士气 |",
        "| --- | --- | --- |",
    ]

    witw_axis_by_name = {u["name"]: u for u in witw["axis_combat"]}
    mod_axis_by_id = {u["ID"]: u for u in mod["axis_combat"]}
    sample_pairs = [
        ("1/15th", "3433", "15. PzGr 第1战斗群"),
        ("2/15th", "3434", "15. PzGr 第2战斗群"),
        ("3/15th", "3435", "15. PzGr 第3战斗群"),
        ("Hermann Goering", "3075", "HG 装甲师 (1/HG 团)"),
        ("29th", "631", "第29装甲掷弹兵师"),
        ("1st", "2044", "第1伞兵师 (空运增援)"),
        ("4th 'Livorno'", "3322", "意大利第4步兵师 Livorno"),
        ("26th 'Assietta'", "3323", "意大利第26步兵师 Assietta"),
        ("54th 'Napoli'", "3345", "意大利第54步兵师 Napoli"),
        ("28th 'Aosta'", "3340", "意大利第28步兵师 Aosta"),
    ]
    for w_name, m_id, label in sample_pairs:
        wu = witw_axis_by_name.get(w_name)
        mu = mod_axis_by_id.get(m_id)
        w_str = f"({wu['x']},{wu['y']}) Del={wu['delay']} Mor={wu['morale']}" if wu else "N/A"
        m_str = f"({mu['X']},{mu['Y']})->Arr({mu['ArriveX']},{mu['ArriveY']}) Del={mu['Delay']} Mor={mu['Morale']}" if mu else "MISSING"
        lines.append(f"| {label} | {w_str} | {m_str} |")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="对比官方 WITW Husky CSV 与本仓库裁剪结果")
    parser.add_argument("--witw-dir", type=Path, default=DEFAULT_WITW_DIR)
    parser.add_argument("--witw-prefix", default=DEFAULT_WITW_PREFIX)
    parser.add_argument("--mod-dir", type=Path, default=DEFAULT_MOD_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    if not (args.witw_dir / f"{args.witw_prefix}_unit.csv").exists():
        raise FileNotFoundError(f"未找到官方 WITW CSV: {args.witw_dir}")
    witw = load_witw_husky(args.witw_dir, args.witw_prefix)
    mod = load_mod_husky(args.mod_dir)
    md = build_comparison_md(witw, mod)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    print(f"Generated {args.out} (WITW unfrozen={len(witw['unfrozen_allied_divs'])}, MOD unfrozen={len(mod['unfrozen_allied_divs'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
