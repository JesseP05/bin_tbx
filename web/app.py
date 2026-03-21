

import json
import time
import os
from flask import Flask, render_template, request
from shared.models import Job


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        job_id = time.time_ns()

        fastq_file = request.files.get('fastq-file') or None
        fastq_name = fastq_file.name

        job_dir = f"shared/data/{job_id}"
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
        job = Job(job_id, fastq_path, "pending", fastp=fastp, kraken=kraken)
        job.create_commands()
        job.save()

    return render_template('index.html', title="Pipeline")


@app.route("/about")
def about():
    return render_template('about.html', title="About")


@app.route("/how-to")
def usage():
    return render_template('usage.html', title="How to use")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
