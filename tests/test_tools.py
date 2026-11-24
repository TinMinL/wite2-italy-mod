#!/usr/bin/env python3
"""自动化测试套件：验证 shape2 几何、真实 WitE2 CSV 端到端裁剪与校验、上游基线提取。"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

MOD_ROOT = Path(__file__).resolve().parent.parent
GAME_ROOT = MOD_ROOT.parent
TOOLS_DIR = MOD_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from crop_csv import crop_scenario_csvs, read_csv_rows
from hex_geometry import (
    are_adjacent_shape2,
    get_neighbors_shape2,
    get_neighbors_shape3_wrong,
    hex_distance_shape2,
    in_playable_area,
    validate_husky_geometry,
)
from validate_csv import validate_scenario_csvs


class TestHexGeometry(unittest.TestCase):
    def test_upstream_husky_coastline_fix_exact_neighbors(self) -> None:
        fix_path = MOD_ROOT / "source" / "witw-wite-v0.9.60" / "data" / "husky-coastline-fix.json"
        fix = json.loads(fix_path.read_text(encoding="utf-8"))
        ng = fix["native_geometry"]

        for key in ("rejected_inland_target", "actual_coastal_target"):
            case = ng[key]
            expected = [tuple(p) for p in case["neighbors"]]
            actual = get_neighbors_shape2(*case["xy"])
            self.assertEqual(actual, expected, msg=f"shape2 neighbors mismatch for {key}")

        # 确认 shape3（按列错位）与真实数据不一致
        wrong_neighbors = get_neighbors_shape3_wrong(149, 293)
        expected_149_293 = [tuple(p) for p in ng["rejected_inland_target"]["neighbors"]]
        self.assertNotEqual(wrong_neighbors, expected_149_293)

    def test_husky_config_validation_passes(self) -> None:
        cfg = json.loads((MOD_ROOT / "config" / "italy_husky_43.json").read_text(encoding="utf-8"))
        errors = validate_husky_geometry(cfg["husky_validation"])
        self.assertEqual(errors, [])

    def test_playable_bounds_half_open(self) -> None:
        nw, se = [104, 208], [176, 318]
        self.assertTrue(in_playable_area(104, 208, nw, se))
        self.assertTrue(in_playable_area(175, 317, nw, se))
        self.assertFalse(in_playable_area(176, 317, nw, se))
        self.assertFalse(in_playable_area(175, 318, nw, se))

    def test_hex_distance_symmetry(self) -> None:
        self.assertEqual(hex_distance_shape2((147, 293), (147, 294)), 1)
        self.assertTrue(are_adjacent_shape2((149, 293), (149, 294)))
        self.assertEqual(hex_distance_shape2((147, 293), (150, 303)), hex_distance_shape2((150, 303), (147, 293)))


class TestRealCsvCropAndValidate(unittest.TestCase):
    def test_velikie_luki_end_to_end_crop_and_validate(self) -> None:
        csv_dir = GAME_ROOT / "Dat" / "CSV"
        prefix = "Introductory Scenario 1 - Velikie Luki"
        self.assertTrue((csv_dir / f"{prefix}_unit.csv").exists(), "Missing sample WitE2 CSV directory")

        # 设定一个小裁剪盒（覆盖 Velikie Luki 核心战区 [194..206) x [124..134)，把 OKH (189,131) 留在框外以测 HQ 自动迁移）
        test_cfg = {
            "scenario_id": "test_vl_crop",
            "map_nw_limit": [194, 124],
            "map_se_limit": [206, 134],
            "high_command_anchor": {
                "axis": {"xy": [195, 131]},
                "allied": {"xy": [202, 128]},
            },
        }

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "cropped"
            # 1. dry-run 不写入输出文件
            dry_report = crop_scenario_csvs(
                input_dir=csv_dir,
                prefix=prefix,
                config=test_cfg,
                output_dir=out_dir,
                dry_run=True,
                relocate_offmap_hqs=True,
            )
            self.assertFalse(out_dir.exists())
            self.assertGreater(dry_report["units_kept"], 0)
            self.assertGreater(dry_report["cities_economy_stripped"], 0)
            self.assertGreater(len(dry_report["hq_relocate_required"]), 0)

            # 2. 实际裁剪并校验输出结构与内容
            real_report = crop_scenario_csvs(
                input_dir=csv_dir,
                prefix=prefix,
                config=test_cfg,
                output_dir=out_dir,
                dry_run=False,
                relocate_offmap_hqs=True,
            )
            self.assertEqual(real_report["units_kept"], dry_report["units_kept"])

            # 核对表头与总行数（槽位索引）严格保持不变
            for suffix in ("unit", "airgroup", "city"):
                in_hdr, in_rows = read_csv_rows(csv_dir / f"{prefix}_{suffix}.csv")
                out_hdr, out_rows = read_csv_rows(out_dir / f"{prefix}_{suffix}.csv")
                self.assertEqual(out_hdr, in_hdr, msg=f"{suffix} header changed")
                self.assertEqual(len(out_rows), len(in_rows), msg=f"{suffix} row count changed")

            # 核对 Berlin（框外城市）工厂与资源已清零
            _, out_cities = read_csv_rows(out_dir / f"{prefix}_city.csv")
            berlin = next(c for c in out_cities if c["name"] == "Berlin")
            self.assertEqual(berlin["factory 0"], "0")
            self.assertEqual(berlin["supplyStore"], "0")

            # 3. 离线校验器对裁剪结果应零报错（允许少量警告如空 hhq=0 高司）
            val = validate_scenario_csvs(out_dir, prefix, test_cfg)
            self.assertEqual(val["errors"], [], msg=f"Unexpected validation errors: {val['errors']}")


class TestBaselineArtifact(unittest.TestCase):
    def test_baseline_json_exists_and_complete(self) -> None:
        baseline_path = MOD_ROOT / "data" / "italy_extracted_baseline.json"
        self.assertTrue(baseline_path.exists())
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        self.assertEqual(data["husky"]["board_shape"], 2)
        self.assertEqual(len(data["husky"]["airborne_plans"]), 7)
        self.assertGreaterEqual(data["victory_points"]["italy_city_count"], 10)


if __name__ == "__main__":
    unittest.main()
