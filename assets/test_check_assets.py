import tempfile
import unittest
from pathlib import Path

import check_assets as ca

GOOD = {
    "key": "prop.tweezers", "kind": "prop", "name": "tweezers.png", "drive_id": "d1",
    "md5": "a" * 32, "hf_media_id": "6ec81b2e-96d1-4377-bac4-716c89242a8f", "status": "confirmed",
    "confirmed_by": "ts", "confirmed_at": "2026-11-11", "quote": "확정본",
}


def cat(assets=(), retired=(), banned=()):
    return ca.Catalog(list(assets), list(retired), list(banned))


class CatalogRules(unittest.TestCase):
    def test_good_asset_passes(self):
        self.assertEqual(ca.check_catalog(cat([GOOD])), [])

    def test_confirmed_needs_quote(self):
        a = {**GOOD, "quote": ""}
        self.assertTrue(any("quote" in e for e in ca.check_catalog(cat([a]))))

    def test_drive_id_required(self):
        a = {**GOOD, "drive_id": ""}
        self.assertTrue(any("drive_id" in e for e in ca.check_catalog(cat([a]))))

    def test_duplicate_key_and_md5(self):
        b = {**GOOD, "name": "other.png"}
        errs = ca.check_catalog(cat([GOOD, b]))
        self.assertTrue(any("key 중복" in e for e in errs))
        self.assertTrue(any("md5 중복" in e for e in errs))

    def test_retired_cannot_equal_live(self):
        r = {"md5": GOOD["md5"], "reason": "x"}
        self.assertTrue(any("현재본과 같은" in e for e in ca.check_catalog(cat([GOOD], [r]))))

    def test_retired_replaced_by_must_exist(self):
        r = {"name": "old.png", "reason": "x", "replaced_by": "nope"}
        self.assertTrue(any("목록에 없다" in e for e in ca.check_catalog(cat([GOOD], [r]))))

    def test_blockout_render_needs_version(self):
        a = {**GOOD, "kind": "blockout_render", "key": "bo.x", "md5": "b" * 32}
        self.assertTrue(any("blockout" in e for e in ca.check_catalog(cat([a]))))


class PromptInputs(unittest.TestCase):
    def page(self, **inp):
        return {"generations": [{"id": "G1", "status": "생성 대기", "inputs": [{"tag": "@image1", **inp}]}]}

    def test_ok(self):
        c = cat([GOOD])
        self.assertEqual(ca.check_prompt_inputs(c, self.page(asset="prop.tweezers", md5="a" * 32)), [])

    def test_missing_asset_key_fails(self):
        errs = ca.check_prompt_inputs(cat([GOOD]), self.page(path="x.png"))
        self.assertTrue(any("asset 키 없음" in e for e in errs))

    def test_retired_name_fails(self):
        c = cat([GOOD], [{"name": "old.png", "reason": "r"}])
        errs = ca.check_prompt_inputs(c, self.page(asset="prop.tweezers", file="a/b/old.png"))
        self.assertTrue(any("폐기된 자료" in e for e in errs))

    def test_banned_prefix_fails(self):
        c = cat([GOOD], banned=[{"path_prefix": "sheets/", "reason": "r"}])
        errs = ca.check_prompt_inputs(c, self.page(asset="prop.tweezers", path="sheets/a.png"))
        self.assertTrue(any("읽기 금지" in e for e in errs))

    def test_retired_stem_matches_png_file(self):
        c = cat([GOOD], [{"name": "old_sheet", "reason": "r"}])
        errs = ca.check_prompt_inputs(c, self.page(asset="prop.tweezers", file="a/old_sheet.png"))
        self.assertTrue(any("폐기된 자료" in e for e in errs))

    def test_banned_prefix_checked_on_file_too(self):
        c = cat([GOOD], banned=[{"path_prefix": "/mnt/project-files/", "reason": "r"}])
        errs = ca.check_prompt_inputs(
            c, self.page(asset="prop.tweezers", path="drive/ok.png", file="/mnt/project-files/t.png"))
        self.assertTrue(any("읽기 금지" in e for e in errs))

    def test_mismatched_md5_fails(self):
        errs = ca.check_prompt_inputs(cat([GOOD]), self.page(asset="prop.tweezers", md5="c" * 32))
        self.assertTrue(any("다르다" in e for e in errs))

    def test_temp_asset_fails(self):
        t = {**GOOD, "status": "temp"}
        errs = ca.check_prompt_inputs(cat([t]), self.page(asset="prop.tweezers"))
        self.assertTrue(any("확정본이 아니다" in e for e in errs))

    def test_done_generation_skipped(self):
        p = self.page(path="x.png")
        p["generations"][0]["status"] = "완료"
        self.assertEqual(ca.check_prompt_inputs(cat([GOOD]), p), [])


class DocScan(unittest.TestCase):
    def test_flags_retired_name_in_docs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "workflow").mkdir()
            (root / "workflow" / "a.md").write_text("시트는 old.png 를 쓴다", encoding="utf-8")
            errs = ca.scan_docs(cat(retired=[{"name": "old.png", "reason": "r"}]), root)
            self.assertEqual(len(errs), 1)


if __name__ == "__main__":
    unittest.main()
