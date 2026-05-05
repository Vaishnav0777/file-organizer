"""Tests for the file organizer."""

import json
from pathlib import Path

import pytest

from src.organizer import build_move_plan, execute_plan, get_category, save_log, undo


# ---------------------------------------------------------------------------
# get_category
# ---------------------------------------------------------------------------
class TestGetCategory:
    def test_image_extensions(self):
        assert get_category(".jpg") == "Images"
        assert get_category(".PNG") == "Images"  # case-insensitive

    def test_document_extensions(self):
        assert get_category(".pdf") == "Documents"
        assert get_category(".docx") == "Documents"

    def test_code_extensions(self):
        assert get_category(".py") == "Code"
        assert get_category(".js") == "Code"

    def test_unknown_extension(self):
        assert get_category(".xyz") == "Other"
        assert get_category(".abc123") == "Other"

    def test_empty_extension(self):
        assert get_category("") == "Other"


# ---------------------------------------------------------------------------
# build_move_plan
# ---------------------------------------------------------------------------
class TestBuildMovePlan:
    def test_creates_plan_for_files(self, tmp_path: Path):
        (tmp_path / "photo.jpg").touch()
        (tmp_path / "report.pdf").touch()
        (tmp_path / "song.mp3").touch()

        plan = build_move_plan(tmp_path)

        assert len(plan) == 3
        categories = {entry["category"] for entry in plan}
        assert categories == {"Images", "Documents", "Audio"}

    def test_skips_directories(self, tmp_path: Path):
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file.txt").touch()

        plan = build_move_plan(tmp_path)
        assert len(plan) == 1

    def test_skips_hidden_files(self, tmp_path: Path):
        (tmp_path / ".hidden").touch()
        (tmp_path / "visible.txt").touch()

        plan = build_move_plan(tmp_path)
        assert len(plan) == 1
        assert "visible" in plan[0]["src"]

    def test_handles_name_collision(self, tmp_path: Path):
        (tmp_path / "Images").mkdir()
        (tmp_path / "Images" / "photo.jpg").touch()
        (tmp_path / "photo.jpg").touch()

        plan = build_move_plan(tmp_path)
        assert "photo_1.jpg" in plan[0]["dest"]

    def test_empty_directory(self, tmp_path: Path):
        plan = build_move_plan(tmp_path)
        assert plan == []


# ---------------------------------------------------------------------------
# execute_plan + undo round-trip
# ---------------------------------------------------------------------------
class TestExecuteAndUndo:
    def test_moves_files(self, tmp_path: Path):
        (tmp_path / "notes.txt").write_text("hello")
        plan = build_move_plan(tmp_path)

        execute_plan(plan)

        assert (tmp_path / "Documents" / "notes.txt").exists()
        assert not (tmp_path / "notes.txt").exists()

    def test_dry_run_does_not_move(self, tmp_path: Path):
        (tmp_path / "notes.txt").write_text("hello")
        plan = build_move_plan(tmp_path)

        execute_plan(plan, dry_run=True)

        assert (tmp_path / "notes.txt").exists()
        assert not (tmp_path / "Documents").exists()

    def test_undo_restores_files(self, tmp_path: Path):
        (tmp_path / "song.mp3").touch()
        (tmp_path / "pic.png").touch()

        plan = build_move_plan(tmp_path)
        execute_plan(plan)
        save_log(tmp_path, plan)

        undo(tmp_path)

        assert (tmp_path / "song.mp3").exists()
        assert (tmp_path / "pic.png").exists()
        assert not (tmp_path / "Audio").exists()
        assert not (tmp_path / "Images").exists()


# ---------------------------------------------------------------------------
# save_log
# ---------------------------------------------------------------------------
class TestSaveLog:
    def test_creates_json_log(self, tmp_path: Path):
        plan = [{"src": "/a/b.txt", "dest": "/a/Docs/b.txt", "category": "Documents"}]
        log_path = save_log(tmp_path, plan)

        assert log_path.exists()
        data = json.loads(log_path.read_text())
        assert "timestamp" in data
        assert len(data["moves"]) == 1
