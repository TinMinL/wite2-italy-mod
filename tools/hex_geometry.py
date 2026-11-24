#!/usr/bin/env python3
"""WitE2 原生 shape2 六角格几何与可玩区边界判定工具。

依据 WITW+WITE v0.9.60 实机校验（husky-coastline-fix.json）：
- WitE2 地图采用 **shape2（按行奇偶错位 / odd-r offset）**，即奇数行（y % 2 == 1）向右错位半格。
- 绝对不要使用按列错位的 shape3 模型（曾导致上游 v0.9.44/v0.9.45 误判内陆格 (149, 293) 为海滩）。
- Map NW/SE Limit 的实际有效区域为半开区间：[NW_x, SE_x) × [NW_y, SE_y)。
"""

from __future__ import annotations

from typing import Iterable, Sequence

# 偶行 (y % 2 == 0) 与 奇行 (y % 2 == 1) 的 6 邻格偏移，顺序：[E, SE, SW, W, NW, NE]
_EVEN_ROW_OFFSETS: tuple[tuple[int, int], ...] = (
    (1, 0),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
)

_ODD_ROW_OFFSETS: tuple[tuple[int, int], ...] = (
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 0),
    (0, -1),
    (1, -1),
)


def get_neighbors_shape2(x: int, y: int) -> list[tuple[int, int]]:
    """返回 WitE2 原生 shape2（odd-r row parity）下 (x, y) 的六个邻格。"""
    offsets = _ODD_ROW_OFFSETS if (y & 1) else _EVEN_ROW_OFFSETS
    return [(x + dx, y + dy) for dx, dy in offsets]


def are_adjacent_shape2(p1: Sequence[int], p2: Sequence[int]) -> bool:
    """判定两格在原生 shape2 几何下是否相邻（不含自身）。"""
    x2, y2 = int(p2[0]), int(p2[1])
    return (x2, y2) in get_neighbors_shape2(int(p1[0]), int(p1[1]))


def _odd_r_to_cube(x: int, y: int) -> tuple[int, int, int]:
    """将 odd-r 偏移坐标转换为立方坐标 (q, r, s) 以便精确计算距离。"""
    q = x - ((y - (y & 1)) // 2)
    r = y
    s = -q - r
    return q, r, s


def hex_distance_shape2(p1: Sequence[int], p2: Sequence[int]) -> int:
    """计算 WitE2 shape2 网格上的最短六角格步数距离。"""
    q1, r1, s1 = _odd_r_to_cube(int(p1[0]), int(p1[1]))
    q2, r2, s2 = _odd_r_to_cube(int(p2[0]), int(p2[1]))
    return max(abs(q1 - q2), abs(r1 - r2), abs(s1 - s2))


def in_playable_area(x: int, y: int, nw: Sequence[int], se: Sequence[int]) -> bool:
    """判定 (x, y) 是否位于 Map NW/SE Limit 有效可玩区内。

    WitE2/WITW 编辑器手册明确规定：实际可玩边界比 SE Limit 小 1，
    即有效范围是 nw[0] <= x < se[0] 且 nw[1] <= y < se[1]。
    """
    return int(nw[0]) <= int(x) < int(se[0]) and int(nw[1]) <= int(y) < int(se[1])


def validate_husky_geometry(husky_cfg: dict) -> list[str]:
    """核对配置文件中的 Husky 两栖海滩与空降目标在 shape2 下的邻接关系。"""
    errors: list[str] = []
    landings = {item["tf_id"]: item for item in husky_cfg.get("landings", [])}
    beach_coords = {tuple(item["target"]) for item in landings.values()}

    for tf_id, info in landings.items():
        tgt = tuple(info["target"])
        app = tuple(info["sea_approach"])
        if not are_adjacent_shape2(tgt, app):
            errors.append(f"TF {tf_id}: beach {tgt} not adjacent to sea_approach {app} under shape2")

    seen_drops: set[tuple[int, int]] = set()
    for plan in husky_cfg.get("airborne_plans", []):
        drop = tuple(plan["target"])
        tf_id = plan["supporting_tf"]
        if drop in beach_coords:
            errors.append(f"Airborne {plan.get('unit', plan.get('id'))} target {drop} overlaps invasion beach")
        if drop in seen_drops:
            errors.append(f"Airborne {plan.get('unit', plan.get('id'))} target {drop} duplicated")
        seen_drops.add(drop)
        if tf_id not in landings:
            errors.append(f"Airborne {plan.get('unit', plan.get('id'))} references missing TF {tf_id}")
        else:
            beach = tuple(landings[tf_id]["target"])
            if not are_adjacent_shape2(drop, beach):
                errors.append(
                    f"Airborne {plan.get('unit', plan.get('id'))} target {drop} not adjacent to TF {tf_id} beach {beach}"
                )
    return errors


def get_neighbors_shape3_wrong(x: int, y: int) -> list[tuple[int, int]]:
    """[反例保留] 按列奇偶错位的 shape3 模型，仅用于单元测试对比，切勿用于剧本判定！"""
    if x & 1:
        offsets = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (0, -1))
    else:
        offsets = ((1, -1), (1, 0), (0, 1), (-1, 0), (-1, -1), (0, -1))
    return [(x + dx, y + dy) for dx, dy in offsets]


if __name__ == "__main__":
    print("Neighbors of (149, 293) shape2:", get_neighbors_shape2(149, 293))
    print("Neighbors of (147, 293) shape2:", get_neighbors_shape2(147, 293))
