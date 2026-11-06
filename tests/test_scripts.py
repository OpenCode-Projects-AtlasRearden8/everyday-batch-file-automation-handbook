"""Tests for The Everyday Batch-File Automation Handbook.

These tests exist for the same reason the book exists: recipes you can trust.
Run them with:
    python -m unittest discover -s tests
"""
import csv
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def run_script(main_fn, argv):
    main_fn(argv)
    return None


class TempCase(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="bfah-"))
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)

    def touch(self, name, data=b""):
        p = self.dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            p.write_text(data, encoding="utf-8")
        else:
            p.write_bytes(data)
        return p

    def run_main(self, module_name, argv):
        mod = __import__(module_name)
        try:
            return mod.main(argv)
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 1


class TestBatchRename(TempCase):
    def test_dry_run_is_default_and_changes_nothing(self):
        a = self.touch("IMG_1.jpg")
        b = self.touch("IMG_2.jpg")
        rc = self.run_main("batch_rename", [str(self.dir), "--action", "replace", "--old", "IMG_", "--old2", "IMG-"])
        self.assertEqual(rc, 0)
        self.assertTrue(a.exists())  # dry run: untouched
        self.assertEqual(a.name, "IMG_1.jpg")
        self.assertTrue(b.exists())

    def test_replace_with_do_it_renames(self):
        a = self.touch("IMG_1.jpg")
        b = self.touch("IMG_2.jpg")
        rc = self.run_main("batch_rename", [str(self.dir), "--action", "replace", "--old", "IMG_", "--old2", "IMG-", "--do-it"])
        self.assertEqual(rc, 0)
        self.assertFalse(a.exists())
        self.assertTrue((self.dir / "IMG-1.jpg").exists())
        self.assertTrue((self.dir / "IMG-2.jpg").exists())

    def test_prefix_and_match_and_case(self):
        self.touch("a.jpg")
        self.touch("b.jpg")
        self.touch("c.txt")
        self.run_main("batch_rename", [str(self.dir), "--action", "prefix", "--chunk", "2026-11 ", "--match", "*.jpg", "--do-it"])
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["2026-11 a.jpg", "2026-11 b.jpg", "c.txt"])
        self.run_main("batch_rename", [str(self.dir), "--action", "upper", "--do-it"])
        self.assertEqual(sorted(str(p) for p in self.dir.iterdir()),
                         sorted(str(self.dir / n) for n in ["2026-11 A.JPG", "2026-11 B.JPG", "C.TXT"]))

    def test_sequence_renames_sorted_files(self):
        self.touch("zeta.jpg")
        self.touch("alpha.jpg")
        self.touch("mid.jpg")
        rc = self.run_main("batch_rename", [str(self.dir), "--action", "sequence", "--chunk", "Report_{:04d}", "--match", "*.jpg", "--do-it"])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()),
                         ["Report_0001.jpg", "Report_0002.jpg", "Report_0003.jpg"])

    def test_collision_cancels_everything(self):
        self.touch("A.txt")
        self.touch("a.txt")
        self.touch("letter-b.txt")
        rc = self.run_main("batch_rename", [str(self.dir), "--action", "lower", "--do-it"])
        self.assertEqual(rc, 2, "collision must cancel, not overwrite")
        names = sorted(p.name for p in self.dir.iterdir())
        self.assertIn("letter-b.txt", names, "files must be untouched after a cancelled run")
        self.assertIn("A.txt", names)

    def test_sequence_needs_a_placeholder(self):
        self.touch("a.txt")
        rc = self.run_main("batch_rename", [str(self.dir), "--action", "sequence", "--chunk", "plain_name", "--do-it"])
        self.assertNotEqual(rc, 0, "a pattern without a { } placeholder should be refused, not silently numbered")
        self.assertTrue((self.dir / "a.txt").exists())

    def test_no_overwrite_of_existing_files(self):
        a = self.touch("IMG_1.jpg")
        self.touch("IMG-1.jpg")
        rc = self.run_main("batch_rename", [str(self.dir), "--action", "replace", "--old", "IMG_", "--old2", "IMG-", "--do-it"])
        self.assertEqual(rc, 2)
        self.assertTrue((self.dir / "IMG-1.jpg").exists(), "pre-existing file must survive")
        self.assertTrue((self.dir / (a.name)).exists() or not a.exists())
        self.assertTrue(a.exists())


class TestJoinCsv(TempCase):
    def test_dry_run_writes_nothing(self):
        data = "date,amount\n2026-01-02,10\n"
        self.touch("jan.csv", data)
        self.touch("feb.csv", data)
        out = self.dir / "q1.csv"
        rc = self.run_main("join_csv", [str(self.dir), "--out", str(out)])
        self.assertEqual(rc, 0)
        self.assertFalse(out.exists())

    def test_join_and_roundtrip_with_split(self):
        self.touch("a.csv", "date,amount\n01,10\n02,20\n")
        self.touch("b.csv", "date,amount\n03,30\n")
        out = self.dir / "total.csv"
        rc = self.run_main("join_csv", [str(self.dir), "--out", str(out), "--do-it"])
        self.assertEqual(rc, 0)
        rows = list(csv.reader(out.open(newline="")))
        self.assertEqual(rows, [["date", "amount"], ["01", "10"], ["02", "20"], ["03", "30"]])

        split_dir = self.dir / "pieces"
        split_dir.mkdir()
        rc = self.run_main("split_csv", [str(out), "--rows", "2", "--out", str(split_dir), "--do-it"])
        self.assertEqual(rc, 0)
        pieces = sorted(p.name for p in split_dir.iterdir())
        self.assertEqual(pieces, ["total_001.csv", "total_002.csv"])
        back = out.with_name("roundtrip.csv")
        rc = self.run_main("join_csv", [str(split_dir), "--out", str(back), "--do-it"])
        self.assertEqual(rc, 0)
        self.assertEqual(list(csv.reader(back.open(newline=""))), rows, "split then join must restore the original")

    def test_refuses_to_overwrite_or_eat_itself(self):
        self.touch("a.csv", "header\n1\n")
        out = self.dir / "a.csv"
        rc = self.run_main("join_csv", [str(self.dir), "--out", str(out), "--do-it"])
        self.assertNotEqual(rc, 0)
        with out.open() as f:
            self.assertEqual(f.read(), "header\n1\n", "existing file must not be clobbered")
        out2 = self.dir / "new.csv"
        rc = self.run_main("join_csv", [str(self.dir), "--out", str(out2), "--do-it"])
        rc3 = self.run_main("join_csv", [str(self.dir), "--out", str(out2), "--do-it"])
        self.assertNotEqual(rc3, 0)

    def test_header_mismatch_files_are_skipped_not_merged(self):
        self.touch("a.csv", "date,amount\n01,10\n")
        self.touch("bad.csv", "day,total\n15,5\n")
        out = self.dir / "out.csv"
        rc = self.run_main("join_csv", [str(self.dir), "--out", str(out), "--do-it"])
        self.assertEqual(rc, 0, "mismatch is reported, not fatal")
        rows = list(csv.reader(out.open(newline="")))
        self.assertEqual(rows, [["date", "amount"], ["01", "10"]], "mismatched file must be excluded")


class TestSplitCsv(TempCase):
    def test_dry_run_writes_nothing(self):
        big = self.touch("big.csv", "h\n" + "\n".join(str(i) for i in range(10)) + "\n")
        rc = self.run_main("split_csv", [str(big), "--rows", "3"])
        self.assertEqual(rc, 0)
        self.assertEqual(list(self.dir.iterdir()), [big])

    def test_splits_with_header_each_piece(self):
        big = self.touch("big.csv", "h\n1\n2\n3\n4\n")
        rc = self.run_main("split_csv", [str(big), "--rows", "2", "--do-it"])
        self.assertEqual(rc, 0)
        p1 = list(csv.reader((self.dir / "big_001.csv").open(newline="")))
        p2 = list(csv.reader((self.dir / "big_002.csv").open(newline="")))
        self.assertEqual(p1, [["h"], ["1"], ["2"]])
        self.assertEqual(p2, [["h"], ["3"], ["4"]])

    def test_writing_twice_is_refused(self):
        big = self.touch("big.csv", "h\n1\n2\n")
        rc = self.run_main("split_csv", [str(big), "--rows", "1", "--do-it"])
        self.assertEqual(rc, 0)
        rc2 = self.run_main("split_csv", [str(big), "--rows", "1", "--do-it"])
        self.assertNotEqual(rc2, 0, "second run must refuse, not overwrite piece 001")
        self.assertEqual(list(csv.reader((self.dir / "big_001.csv").open(newline=""))), [["h"], ["1"]])


class TestPdfTools(TempCase):
    def setUp(self):
        super().setUp()
        try:
            from pypdf import PdfReader  # noqa: F401
            from reportlab.pdfgen import canvas
            self.has_pypdf = True

            def make_pdf(name, tag):
                path = self.dir / name
                c = canvas.Canvas(str(path))
                c.drawString(72, 720, f"Page in {tag}")
                c.showPage()
                c.drawString(72, 720, f"Page two of {tag}")
                c.showPage()
                c.save()
                return path

            self.make_pdf = make_pdf
        except ImportError:
            self.has_pypdf = False

    def tearDown(self):
        super().tearDown()

    def test_join_dry_run_and_merge(self):
        if not self.has_pypdf:
            self.skipTest("pypdf/reportlab not installed")
        from pypdf import PdfReader
        a, b = self.make_pdf("a.pdf", "A"), self.make_pdf("b.pdf", "B")
        out = self.dir / "m.pdf"
        rc = self.run_main("join_pdfs", [str(a), str(b), "--out", str(out)])
        self.assertEqual(rc, 0)
        self.assertFalse(out.exists())
        rc = self.run_main("join_pdfs", [str(a), str(b), "--out", str(out), "--do-it"])
        self.assertEqual(rc, 0)
        merged = PdfReader(str(out))
        self.assertEqual(len(merged.pages), 4, "2-page PDF + 2-page PDF = 4 pages")

    def test_split_single_pages(self):
        if not self.has_pypdf:
            self.skipTest("pypdf/reportlab not installed")
        from pypdf import PdfReader
        src = self.make_pdf("table.pdf", "T")
        outdir = self.dir / "chunks"
        outdir.mkdir()
        rc = self.run_main("split_pdfs", [str(src), "--every", "1", "--out", str(outdir), "--do-it"])
        self.assertEqual(rc, 0)
        pieces = sorted(outdir.iterdir())
        self.assertEqual(len(pieces), 2)
        for piece in pieces:
            self.assertEqual(len(PdfReader(str(piece)).pages), 1)

    def test_nonexistent_output_refused_to_be_overwritten(self):
        if not self.has_pypdf:
            self.skipTest("pypdf/reportlab not installed")
        a = self.make_pdf("a.pdf", "A")
        out = self.dir / "m.pdf"
        out.write_bytes(b"precious")
        rc = self.run_main("join_pdfs", [str(a), "--out", str(out), "--do-it"])
        self.assertNotEqual(rc, 0)
        self.assertEqual(out.read_bytes(), b"precious")


class TestImageTools(TempCase):
    def setUp(self):
        super().setUp()
        try:
            from PIL import Image
            self.Image = Image
            self.has_pil = True
        except ImportError:
            self.has_pil = False

    def test_resize_dry_run_and_do_it(self):
        if not self.has_pil:
            self.skipTest("Pillow not installed")
        Image = self.Image
        big = self.dir / "photo.jpg"
        Image.new("RGB", (2000, 1000), "red").save(big)
        rc = self.run_main("resize_images", [str(self.dir), "--max-edge", "500"])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["photo.jpg"])
        rc = self.run_main("resize_images", [str(self.dir), "--max-edge", "500", "--do-it"])
        self.assertEqual(rc, 0)
        with Image.open(self.dir / "photo_small.jpg") as im:
            self.assertEqual(im.size, (500, 250), "aspect ratio kept")
        with Image.open(big) as im:
            self.assertEqual(im.size, (2000, 1000), "original untouched by default")

    def test_convert_never_touches_original(self):
        if not self.has_pil:
            self.skipTest("Pillow not installed")
        Image = self.Image
        Image.new("RGB", (10, 10), "blue").save(self.dir / "a.png")
        rc = self.run_main("convert_images", [str(self.dir), "--to", "webp"])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["a.png"])
        rc = self.run_main("convert_images", [str(self.dir), "--to", "webp", "--do-it"])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["a.png", "a.webp"])
        with Image.open(self.dir / "a.webp") as im:
            self.assertEqual(im.format, "WEBP")
        with Image.open(self.dir / "a.png") as im:
            self.assertEqual(im.format, "PNG")


class TestSortFolder(TempCase):
    def test_dry_run_moves_nothing(self):
        self.touch("photo.jpg")
        self.touch("note.txt")
        self.touch("blob.xyz")
        dirs_before = [p for p in self.dir.iterdir() if p.is_dir()]
        rc = self.run_main("sort_folder", [str(self.dir)])
        self.assertEqual(rc, 0)
        self.assertEqual([p for p in self.dir.iterdir() if p.is_dir()], dirs_before)
        self.assertTrue((self.dir / "photo.jpg").exists())

    def test_sort_with_unsorted_bucket_and_no_deletion(self):
        names = ["photo.jpg", "cv.pdf", "blob.xyz"]
        for n in names:
            self.touch(n, "x")
        rc = self.run_main("sort_folder", [str(self.dir), "--do-it"])
        self.assertEqual(rc, 0)
        self.assertTrue((self.dir / "images" / "photo.jpg").exists())
        self.assertTrue((self.dir / "documents" / "cv.pdf").exists())
        self.assertTrue((self.dir / "_unsorted" / "blob.xyz").exists(), "unknown types land in _unsorted, never deleted")
        blobs = list(self.dir.rglob("*.xyz"))
        self.assertEqual(len(blobs), 1)

    def test_by_year(self):
        self.touch("old.pdf")
        rc = self.run_main("sort_folder", [str(self.dir), "--by-year", "--do-it"])
        self.assertEqual(rc, 0)
        year_dirs = list((self.dir / "documents").iterdir())
        self.assertEqual(len(year_dirs), 1)
        self.assertTrue(year_dirs[0].name.isdigit())
        self.assertTrue((year_dirs[0] / "old.pdf").exists())

    def test_same_name_files_are_not_lost(self):
        (self.dir / "sub").mkdir()
        (self.dir / "sub" / "same.txt").write_text("A", encoding="utf-8")
        self.touch("same.txt", "B")
        rc = self.run_main("sort_folder", [str(self.dir), "--do-it"])
        self.assertTrue((self.dir / "sub" / "same.txt").exists(), "already in subfolder: untouched (loose files only)")
        moved = list((self.dir / "documents").iterdir())
        self.assertEqual([p.name for p in moved], ["same.txt"])


class TestDocsAndLicense(unittest.TestCase):
    DOCS = ROOT / "docs"

    @classmethod
    def doc_names(cls):
        return sorted(p.name for p in cls.DOCS.glob("*.md"))

    def test_all_chapters_exist(self):
        expected = [
            "01-start-here.md", "02-safety-first.md", "03-mass-rename.md",
            "04-csv-join-split.md", "05-pdf-join-split.md", "06-image-resize.md",
            "07-format-conversions.md", "08-folder-rules.md", "09-ai-copilot.md",
            "10-cookbook.md",
        ]
        missing = [n for n in expected if not (self.DOCS / n).exists()]
        self.assertEqual(missing, [], "every promised chapter must exist")

    def test_every_script_referenced_in_docs_exists(self):
        import re
        pattern = re.compile(r"scripts/([A-Za-z0-9_]+\.py)")
        referenced = set()
        for doc in self.DOCS.glob("*.md"):
            referenced |= set(pattern.findall(doc.read_text(encoding="utf-8")))
        readme_scripts = set(pattern.findall((ROOT / "README.md").read_text(encoding="utf-8")))
        all_refs = referenced | readme_scripts
        missing = [s for s in sorted(all_refs) if not (SCRIPTS / s).exists()]
        self.assertEqual(missing, [], "docs must only reference scripts that exist")

    def test_license_exact_copyright(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", text)
        self.assertIn("MIT License", text)

    def test_readme_credits_llc(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", text)
        self.assertIn("MIT", text)


class TestSiteBuild(unittest.TestCase):
    PAGES = ["index.html"] + [n[:-3] + ".html" for n in [
        "01-start-here.md", "02-safety-first.md", "03-mass-rename.md",
        "04-csv-join-split.md", "05-pdf-join-split.md", "06-image-resize.md",
        "07-format-conversions.md", "08-folder-rules.md", "09-ai-copilot.md",
        "10-cookbook.md",
    ]]

    def test_build_site_runs_and_produces_pages(self):
        import subprocess
        result = subprocess.run([sys.executable, "build_site.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        site = ROOT / "site"
        missing = [p for p in self.PAGES if not (site / p).exists()]
        self.assertEqual(missing, [], "site must include every chapter page")
        self.assertIn("Asdale Dynamics, LLC", (site / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
