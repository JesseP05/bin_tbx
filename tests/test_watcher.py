"""test module voor watcher.py"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from shared.models import Job

# ── helpers ──────────────────────────────────────────────────────────────────

def make_job_file(tmp_path, status="pending"):
    job_id = "test_job_123"
    job_dir = tmp_path / job_id
    job_dir.mkdir()
    data = {
        "job_id": job_id,
        "fastq_filename_r1": f"{job_dir}/sample.fastq",
        "fastq_filename_r2": None,
        "filepath": str(job_dir),
        "status": status,
        "fastp_command": "fastp -i input.fastq -o output.fastq",
        "kraken_command": "kraken2 --db /db input.fastq",
        "krona_command": "ktImportTaxonomy input.txt -o output.html",
        "job_size": None,
        "rm_after_fastp": [],
        "rm_after_kraken": [],
        "rm_after_krona": [],
    }
    job_file = job_dir / f"{job_id}_job.json"
    job_file.write_text(json.dumps(data))
    return job_file, data


# ── load_job ──────────────────────────────────────────────────────────────────

def test_load_job_basic(tmp_path):
    from watcher import load_job
    job_file, data = make_job_file(tmp_path)
    job = load_job(str(job_file))
    assert job.job_id == data["job_id"]
    assert job.status == "pending"
    assert job.fastp_command == data["fastp_command"]


def test_load_job_missing_optional_fields(tmp_path):
    """rm_after_* should default to empty list if absent"""
    from watcher import load_job
    job_file, _ = make_job_file(tmp_path)
    data = json.loads(job_file.read_text())
    del data["rm_after_fastp"]
    job_file.write_text(json.dumps(data))

    job = load_job(str(job_file))
    assert job.rm_after_fastp == []


# ── run_tool ──────────────────────────────────────────────────────────────────

def test_run_tool_success(tmp_path):
    from watcher import run_tool
    job_file, _ = make_job_file(tmp_path)

    with patch("watcher.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        job = MagicMock()
        job.rm_after_fastp = []
        result = run_tool(job, "fastp", "fastp -i in.fastq -o out.fastq")

    assert result is True


def test_run_tool_failure_sets_status(tmp_path):
    from watcher import run_tool
    with patch("watcher.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="something went wrong")
        job = MagicMock()
        result = run_tool(job, "fastp", "fastp -i in.fastq -o out.fastq")

    assert result is False
    assert job.status == "failed"
    job.save.assert_called_once()


def test_run_tool_cleans_up_files(tmp_path):
    """Files in rm_after_fastp should be deleted on success"""
    from watcher import run_tool
    dummy_file = tmp_path / "big_intermediate.fastq"
    dummy_file.write_text("data")

    with patch("watcher.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        job = MagicMock()
        job.rm_after_fastp = [str(dummy_file)]
        run_tool(job, "fastp", "fastp ...")

    assert not dummy_file.exists()


# ── process_job ───────────────────────────────────────────────────────────────

def test_process_job_stops_on_failure(tmp_path):
    """If fastp fails, kraken2 and krona should not run"""
    from watcher import process_job

    side_effects = [False, True, True]  # fastp fails
    with patch("watcher.run_tool", side_effect=side_effects) as mock_tool:
        job = MagicMock()
        job.fastp_command = "fastp ..."
        job.kraken_command = "kraken2 ..."
        job.krona_command = "krona ..."
        process_job(job)

    assert mock_tool.call_count == 1


# ── cleanup_files ─────────────────────────────────────────────────────────────

def test_cleanup_files_keeps_job_json(tmp_path):
    from watcher import cleanup_files
    job_dir = tmp_path / "job123"
    job_dir.mkdir()
    (job_dir / "job123_job.json").write_text("{}")
    (job_dir / "big_output.fastq").write_text("data")
    (job_dir / "report.html").write_text("<html>")

    cleanup_files(str(job_dir))

    remaining = list(job_dir.iterdir())
    assert len(remaining) == 1
    assert remaining[0].name == "job123_job.json"


# ── clean_unfinished_jobs ─────────────────────────────────────────────────────

def test_clean_unfinished_jobs_resets_processing(tmp_path):
    from watcher import clean_unfinished_jobs
    import watcher
    original = watcher.JOBS_DIR
    watcher.JOBS_DIR = str(tmp_path)

    job_file, _ = make_job_file(tmp_path, status="processing")
    # also put a dummy file in the dir that should get cleaned
    job_dir = job_file.parent
    (job_dir / "intermediate.fastq").write_text("data")

    clean_unfinished_jobs()

    data = json.loads(job_file.read_text())
    assert data["status"] == "pending"

    watcher.JOBS_DIR = original