

import json
import time
import os
import subprocess
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from shared.models import Job


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        job_id = time.time_ns()
        b_paired = request.form.get("fastp-paired", "0") == "1"
        print(f"Paired-end reads: {int(b_paired)}", flush=True)

        job_dir = f"/data/{job_id}"
        os.makedirs(job_dir, exist_ok=True)

        fastq_path_r1 = None
        fastq_path_r2 = None

        if b_paired:
            fastq_file_r1 = request.files.get("fastq-file-r1")
            fastq_file_r2 = request.files.get("fastq-file-r2")

            fastq_name_r1 = secure_filename(fastq_file_r1.filename)
            fastq_name_r2 = secure_filename(fastq_file_r2.filename)

            fastq_path_r1 = f"{job_dir}/{fastq_name_r1}"
            fastq_path_r2 = f"{job_dir}/{fastq_name_r2}"
            fastq_file_r1.save(fastq_path_r1)
            fastq_file_r2.save(fastq_path_r2)
        else:
            fastq_file = request.files.get("fastq-file-r1")
            fastq_name = secure_filename(fastq_file.filename)

            fastq_path_r1 = f"{job_dir}/{fastq_name}"
            fastq_file.save(fastq_path_r1)

        fastp_kwargs = {
            "min-quality": request.form.get("fastp-quality", 15),
            "trim-adapters": int(request.form.get("fastp-adapter", 1)),
            "length-min": request.form.get("fastp-min-length", 60),
            "length-max": request.form.get("fastp-length-max", 0),
            "cut-front": int(request.form.get("fastp-cut-front", 0)),
            "cut-tail": int(request.form.get("fastp-cut-tail", 0)),
            "deduplicate": int(request.form.get("fastp-dedup", 0)),
            "paired": int(b_paired),
        }

        kraken_kwargs = {
            "confidence": request.form.get("kraken-confidence", 0.0),
            "paired-end": int(request.form.get("kraken-paired", 0)),
            "use-science-names": int(request.form.get("kraken-use-names", 0)),
            "base-quality": request.form.get("kraken-base-quality", 0),
        }

        fastp = Job.FastP(**fastp_kwargs)
        kraken = Job.Kraken(**kraken_kwargs)
        job = Job(
            job_id,
            fastq_filename_r1=fastq_path_r1,
            filepath=job_dir,
            status="pending",
            fastp=fastp,
            kraken=kraken,
            fastq_filename_r2=fastq_path_r2 if b_paired else None
        )
        job.create_commands()
        job.save()
        return render_template('index.html', title="Pipeline", current_job=job_id)

    return render_template('index.html', title="Pipeline", current_job=None)


@app.route("/about")
def about():
    return render_template('about.html', title="About")


@app.route("/how-to")
def usage():
    return render_template('usage.html', title="How to use")


@app.route("/job/<job_id>/status")
def get_job_status(job_id):
    job_dir = f"/data/{job_id}"
    results_file = f"{job_dir}/{job_id}_results.json"
    job_file = f"{job_dir}/{job_id}_job.json"
    
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            return jsonify(json.load(f))
    
    if os.path.exists(job_file):
        with open(job_file, "r") as f:
            data = json.load(f)
            return jsonify({"job_id": job_id, "status": data["status"]})
    
    return jsonify({"error": "Job not found"}), 404


@app.route("/data/<path:filepath>")
def serve_data(filepath):
    data_dir = "/data"
    full_path = os.path.join(data_dir, filepath)

    if not os.path.abspath(full_path).startswith(os.path.abspath(data_dir)):
        return jsonify({"error": "Invalid path"}), 403
    
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(full_path)


@app.route("/history")
def history():
    data_dir = "/data"
    history = []
    for job_dir in os.listdir(data_dir):
        job_path = os.path.join(data_dir, job_dir)
        if os.path.isdir(job_path):
            results_file = os.path.join(job_path, f"{job_dir}_results.json")
            if os.path.exists(results_file):
                with open(results_file, "r") as f:
                    job_data = json.load(f)
                    history.append({
                        "job_id": job_dir,
                        "status": job_data.get("status"),
                        "timestamp": job_data.get("completed_at", 0),
                        "job_size": job_data.get("job_size", "N/A"),
                        "fastp_report": job_data.get("fastq_report"),
                        "krona_output": job_data.get("krona_output"),
                    })
    history.sort(key=lambda x: x["job_id"], reverse=True)
    return render_template('history.html', history=history)


@app.route("/clear-history")
def clear_history():
    data_dir = "/data"
    for job_dir in os.listdir(data_dir):
        job_path = os.path.join(data_dir, job_dir)
        if os.path.isdir(job_path):
            subprocess.run(f"rm -rf {job_path}", shell=True)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
