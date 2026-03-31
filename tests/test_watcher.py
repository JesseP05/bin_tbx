"""test module voor watcher.py"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from shared.models import Job
from watcher import *
import watcher

def fake_job_file(tmp_path, status="pending"):
    job_id = "8008135"
    job_dir = f"{tmp_path}/{job_id}"
    os.makedirs(job_dir, exist_ok=True)
    actual_data = {
        "job_id": job_id,
        "fastq_filename_r1": f"{job_dir}/sample.fastq",
        "fastq_filename_r2": None,
        "filepath": job_dir,
        "status": status,
        "fastp_command": "fastp -i input.fastq -o output.fastq",
        "kraken_command": "kraken2 --db /db input.fastq",
        "krona_command": "ktImportTaxonomy input.txt -o output.html",
        "job_size": None,
        "rm_after_fastp": [],
        "rm_after_kraken": [],
        "rm_after_krona": [],
    }
    job_file = f"{job_dir}/{job_id}_job.json"
    with open(job_file, "w") as f:
        json.dump(actual_data, f, indent=4)
    return job_file, actual_data


def test_load_job(tmp_path):
    job_file, actual_data = fake_job_file(tmp_path)
    job = load_job(job_file)
    assert job.job_id == actual_data["job_id"]
    assert job.status == "pending"
    assert job.fastp_command == actual_data["fastp_command"]


def test_load_job_missing_field(tmp_path):
    """rm_after moet [] zijn als ontbreekt"""
    job_file, actual_data = fake_job_file(tmp_path)
    with open(job_file, "r") as f:
        data = json.load(f)
    del data["rm_after_fastp"]
    with open(job_file, "w") as f:
        json.dump(data, f, indent=4)

    job = load_job(job_file)
    assert job.rm_after_fastp == []


def test_run_tool(tmp_path):
    job_file, _ = fake_job_file(tmp_path)

    with patch("watcher.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        job = MagicMock()
        result = run_tool(job, "fastp", "fastp -i in.fastq -o out.fastq")

    assert result is True


def test_run_tool_set_fails(tmp_path):
    with patch("watcher.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="error")
        job = MagicMock()
        result = run_tool(job, "fastp", "fastp -i in.fastq -o out.fastq")

    assert result is False
    assert job.status == "failed"
    job.save.assert_called_once()


def test_run_tool_cleans_up_files(tmp_path):
    """Files in rm_after_fastp should be deleted on run"""
    dummy_file = f"{tmp_path}/big_intermediate.fastq"
    with open(dummy_file, "w") as f:
        f.write("data")

    with patch("watcher.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        job = MagicMock()
        job.rm_after_fastp = [dummy_file]
        run_tool(job, "fastp", "fastp ...")

    assert not os.path.exists(dummy_file)


def test_process_job_stops_on_failure(tmp_path):
    """als kraken failed stop krona"""

    side_effects = [True, False, True]  # fastp fails
    with patch("watcher.run_tool", side_effect=side_effects) as mock_tool:
        job = MagicMock()
        job.fastp_command = "fastp ..."
        job.kraken_command = "kraken2 ..."
        job.krona_command = "krona ..."
        process_job(job)

    assert mock_tool.call_count == 2
    mock_tool.assert_any_call(job, "fastp", job.fastp_command)
    mock_tool.assert_any_call(job, "kraken2", job.kraken_command)


def test_cleanup_files_keeps_job_json(tmp_path):
    job_dir = f"{tmp_path}/job123"
    os.makedirs(job_dir, exist_ok=True)
    with open(f"{job_dir}/job123_job.json", "w") as f:
        json.dump({}, f)
    with open(f"{job_dir}/big_output.fastq", "w") as f:
        f.write("data")
    with open(f"{job_dir}/report.html", "w") as f:
        f.write("<html>")

    cleanup_files(job_dir)

    remaining = os.listdir(job_dir)
    assert len(remaining) == 1
    assert remaining[0] == "job123_job.json"


def test_clean_unfinished_jobs_resets_processing(tmp_path):
    original = watcher.JOBS_DIR
    watcher.JOBS_DIR = str(tmp_path)

    job_file, _ = fake_job_file(tmp_path, status="processing")
    job_dir = os.path.dirname(job_file)
    with open(job_dir + "/intermediate.fastq", "w") as f:
        f.write("data")

    clean_unfinished_jobs()

    with open(job_file, "r") as f:
        data = json.load(f)
    assert data["status"] == "pending"
    assert not os.path.exists(job_dir + "/intermediate.fastq")

    watcher.JOBS_DIR = original