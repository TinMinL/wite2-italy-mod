#!/usr/bin/env python3
"""自动化测试套件：验证 shape2 几何、Old/New Editor 真实 WitE2 CSV 端到端裁剪与校验、事件变长尾列与编码保真。"""

from __future__ import annotations

import csv
import hashlib
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

from crop_csv import crop_scenario_csvs, detect_csv_encoding, is_unit_slot_alive, read_csv_rows
from hex_geometry import (
    are_adjacent_shape2,
    get_neighbors_shape2,
    get_neighbors_shape3_wrong,
    hex_distance_shape2,
    in_excluded_boxes,
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

        wrong_neighbors = get_neighbors_shape3_wrong(149, 293)
        expected_149_293 = [tuple(p) for p in ng["rejected_inland_target"]["neighbors"]]
        self.assertNotEqual(wrong_neighbors, expected_149_293)

    def test_husky_config_validation_passes(self) -> None:
        cfg = json.loads((MOD_ROOT / "config" / "italy_husky_43.json").read_text(encoding="utf-8"))
        errors = validate_husky_geometry(cfg["husky_validation"])
        self.assertEqual(errors, [])

    def test_playable_bounds_and_exclude_boxes(self) -> None:
        nw, se = [57, 208], [176, 318]
        self.assertTrue(in_playable_area(57, 208, nw, se))
        self.assertTrue(in_playable_area(175, 317, nw, se))
        self.assertFalse(in_playable_area(176, 317, nw, se))
        self.assertFalse(in_playable_area(175, 318, nw, se))

        ex = [{"name": "Balkans", "nw": [147, 208], "se": [176, 252]}]
        self.assertTrue(in_excluded_boxes(153, 223, ex))
        self.assertFalse(in_excluded_boxes(137, 255, ex))

    def test_hex_distance_symmetry(self) -> None:
        self.assertEqual(hex_distance_shape2((147, 293), (147, 294)), 1)
        self.assertTrue(are_adjacent_shape2((149, 293), (149, 294)))
        self.assertEqual(hex_distance_shape2((147, 293), (150, 303)), hex_distance_shape2((150, 303), (147, 293)))


class TestOldEditorCsvCropAndValidate(unittest.TestCase):
    def test_velikie_luki_end_to_end_crop_and_validate(self) -> None:
        csv_dir = GAME_ROOT / "Dat" / "CSV"
        prefix = "Introductory Scenario 1 - Velikie Luki"
        self.assertTrue((csv_dir / f"{prefix}_unit.csv").exists(), "Missing sample Old Editor CSV")

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

            real_report = crop_scenario_csvs(
                input_dir=csv_dir,
                prefix=prefix,
                config=test_cfg,
                output_dir=out_dir,
                dry_run=False,
                relocate_offmap_hqs=True,
            )
            self.assertEqual(real_report["units_kept"], dry_report["units_kept"])

            for suffix in ("unit", "airgroup", "city"):
                in_hdr, in_rows, _ = read_csv_rows(csv_dir / f"{prefix}_{suffix}.csv")
                out_hdr, out_rows, _ = read_csv_rows(out_dir / f"{prefix}_{suffix}.csv")
                self.assertEqual(out_hdr, in_hdr, msg=f"{suffix} header changed")
                self.assertEqual(len(out_rows), len(in_rows), msg=f"{suffix} row count changed")

            _, out_cities, _ = read_csv_rows(out_dir / f"{prefix}_city.csv")
            berlin = next(c for c in out_cities if c["name"] == "Berlin")
            self.assertEqual(berlin["factory 0"], "0")
            self.assertEqual(berlin["supplyStore"], "0")

            val = validate_scenario_csvs(out_dir, prefix, test_cfg)
            self.assertEqual(val["errors"], [], msg=f"Unexpected validation errors: {val['errors']}")


class TestNewEditorRealV0960Pipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.real_dir = GAME_ROOT / "Dat" / "CSV" / "WITW+WITE v0.9.60"
        if not (self.real_dir / "Units.csv").exists():
            self.skipTest("未检测到导出的 Dat/CSV/WITW+WITE v0.9.60 目录")

    def test_real_husky_crop_validate_and_fidelity(self) -> None:
        cfg = json.loads((MOD_ROOT / "config" / "italy_husky_43.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "Italy_Husky_43"
            report = crop_scenario_csvs(
                input_dir=self.real_dir,
                prefix="",
                config=cfg,
                output_dir=out_dir,
                dry_run=False,
                relocate_offmap_hqs=True,
            )
            self.assertEqual(report["editor_layout"], "new")
            self.assertGreater(report["kept_airbases"], 40)
            self.assertGreater(report["airgroups_kept"], 100)

            val = validate_scenario_csvs(out_dir, "", cfg)
            self.assertEqual(val["errors"], [], msg=f"Husky validation errors: {val['errors']}")

            # 验证 6 支两栖 TF 与 7 支空降分队全部存活且未落入排除区
            _, u_rows, _ = read_csv_rows(out_dir / "Units.csv")
            u_by_id = {r["ID"]: r for r in u_rows}
            alive_ids = {r["ID"] for r in u_rows if is_unit_slot_alive(r)}
            for tf in cfg["husky_validation"]["landings"]:
                self.assertIn(str(tf["tf_id"]), alive_ids)
            for ab in cfg["husky_validation"]["airborne_plans"]:
                self.assertIn(str(ab["id"]), alive_ids)

            # WITW 历史校准回归：第29装掷师(631)与第1伞兵师(2044)存活，士气已校准
            self.assertIn("631", alive_ids)
            self.assertEqual(u_by_id["631"]["Morale"], "70")
            self.assertIn("2044", alive_ids)
            self.assertEqual(u_by_id["2044"]["Delay"], "1")
            self.assertEqual((u_by_id["2044"]["ArriveX"], u_by_id["2044"]["ArriveY"]), ("153", "290"))
            self.assertEqual(u_by_id["2044"]["Morale"], "85")
            for hg_id in ("3075", "3163", "3164"):
                self.assertEqual(u_by_id[hg_id]["Morale"], "70")
            for pzg15_id in ("3433", "3434", "3435"):
                self.assertEqual(u_by_id[pzg15_id]["Morale"], "75")

            # 非西西里11支盟军师已冻结 >=12，2nd SAS(11808) 与参战师保持未冻结
            for frz_id in cfg["freeze_unit_ids"]["unit_ids"]:
                self.assertGreaterEqual(int(u_by_id[str(frz_id)]["Frozen"]), 12)
            self.assertEqual(u_by_id["11808"]["Frozen"], "0")
            self.assertEqual(u_by_id["11583"]["Frozen"], "0")

            # 验证 Pilots.csv（ISO-8859-1）字节与 SHA256 原样无损
            src_sha = hashlib.sha256((self.real_dir / "Pilots.csv").read_bytes()).hexdigest()
            dst_sha = hashlib.sha256((out_dir / "Pilots.csv").read_bytes()).hexdigest()
            self.assertEqual(dst_sha, src_sha)

            # 验证 GameEvents.csv 变长每行列数不变，且 24 (Italy Surrenders) 与 78 (Berlin) 已停用
            with (self.real_dir / "GameEvents.csv").open("r", encoding=detect_csv_encoding(self.real_dir / "GameEvents.csv"), newline="") as f:
                src_ev = list(csv.reader(f))
            with (out_dir / "GameEvents.csv").open("r", encoding=detect_csv_encoding(out_dir / "GameEvents.csv"), newline="") as f:
                dst_ev = list(csv.reader(f))
            self.assertEqual([len(r) for r in dst_ev], [len(r) for r in src_ev])
            ev_map = {r[0]: r for r in dst_ev[1:] if r}
            self.assertEqual(ev_map["24"][12], "0")
            self.assertEqual(ev_map["78"][12], "0")

    def test_real_campaign_crop_validate(self) -> None:
        cfg = json.loads((MOD_ROOT / "config" / "italy_campaign_43_45.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "Italy_Campaign_43_45"
            report = crop_scenario_csvs(
                input_dir=self.real_dir,
                prefix="",
                config=cfg,
                output_dir=out_dir,
                dry_run=False,
                relocate_offmap_hqs=True,
            )
            self.assertGreater(report["units_kept"], 500)
            self.assertGreater(report["kept_airbases"], 150)
            self.assertGreater(report["airgroups_kept"], 200)

            val = validate_scenario_csvs(out_dir, "", cfg)
            self.assertEqual(val["errors"], [], msg=f"Campaign validation errors: {val['errors']}")

            # 验证排除区（南法、巴尔干）内存活地图单位数为 0，且第1伞兵师(2044)与XI伞兵军(2014)已豁免保留
            _, u_rows, _ = read_csv_rows(out_dir / "Units.csv")
            alive_ids = {r["ID"] for r in u_rows if is_unit_slot_alive(r)}
            self.assertIn("2044", alive_ids)
            self.assertIn("2014", alive_ids)
            for r in u_rows:
                if is_unit_slot_alive(r) and int(r["X"]) > 0 and int(r["Y"]) > 0:
                    self.assertFalse(in_excluded_boxes(int(r["X"]), int(r["Y"]), cfg["exclude_boxes"]))

            # 验证 78 (Berlin) 已停用而 24 (Italy Surrenders) 仍保持启用
            with (out_dir / "GameEvents.csv").open("r", encoding=detect_csv_encoding(out_dir / "GameEvents.csv"), newline="") as f:
                ev_map = {r[0]: r for r in list(csv.reader(f))[1:] if r}
            self.assertEqual(ev_map["78"][12], "0")
            self.assertEqual(ev_map["24"][12], "1")


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
