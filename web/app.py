

import json
import time
import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
#from shared.models import Job


app = Flask(__name__)

# geen vervelende fetch logs van js
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        job_id = time.time_ns()

        fastq_file = request.files.get('fastq-file') or None
        fastq_name = fastq_file.name

        job_dir = f"/data/{job_id}"
        os.makedirs(job_dir, exist_ok=True)
        
        fastq_path = f"{job_dir}/{fastq_name}.fastq"
        fastq_file.save(fastq_path)

        fastp_kwargs = {
            "min-quality": request.form.get("fastp-quality", 15),
            "trim-adapters": request.form.get("fastp-adapter", 1),
            "length-min": request.form.get("fastp-min-length", 60),
            "length-max": request.form.get("fastp-length-max", 0),
            "cut-front": request.form.get("fastp-cut-front", 0),
            "cut-tail": request.form.get("fastp-cut-tail", 0),
            "deduplicate": request.form.get("fastp-dedup", 0),
        }

        kraken_kwargs = {
            "confidence": request.form.get("kraken-confidence", 0.0),
            "paired-end": request.form.get("kraken-paired", 0),
            "use-science-names": request.form.get("kraken-use-names", 0),
            "base-quality": request.form.get("kraken-base-quality", 0),
        }

        fastp = Job.FastP(**fastp_kwargs)
        kraken = Job.Kraken(**kraken_kwargs)
        job = Job(job_id, fastq_filename=fastq_path, filepath=job_dir, status="pending", fastp=fastp, kraken=kraken)
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
    
    # Security check: ensure the requested path is within /data
    if not os.path.abspath(full_path).startswith(os.path.abspath(data_dir)):
        return jsonify({"error": "Invalid path"}), 403
    
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(full_path)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
