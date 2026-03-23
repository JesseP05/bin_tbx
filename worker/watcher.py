
import json
import time
import os
import subprocess
import atexit
from shared.models import Job


JOBS_DIR = "/data"


class JobResult:
    def __init__(self, job):
        self.job_id = job.job_id
        self.status = "completed"
        self.fastq_report = f"{job.filepath}/{job.job_id}_fastp.html"
        self.fastp_output = f"{job.filepath}/{job.job_id}_fastp_output.fastq"
        self.kraken_report = f"{job.filepath}/{job.job_id}_kraken_report.txt"
        self.kraken_output = f"{job.filepath}/{job.job_id}_kraken_output.txt"
        self.krona_output = f"{job.filepath}/{job.job_id}_krona.html"
        self.completed_at = time.ctime()
    
    def save(self, job_dir):
        with open(f"{job_dir}/{self.job_id}_results.json", "w") as f:
            json.dump(self.__dict__, f, indent=4)


def load_job(job_file):
    with open(job_file, "r") as f:
        data = json.load(f)
    job = Job(
        job_id=data["job_id"],
        fastq_filename=data["fastq_filename"],
        filepath=data["filepath"],
        status=data["status"]
    )
    job.fastp_command = data.get("fastp_command")
    job.kraken_command = data.get("kraken_command")
    job.krona_command = data.get("krona_command")
    return job


def process_job(job):
    job.status = "processing"
    job.save()
    
    try:
        print(f"Running fastp...")
        result = subprocess.run(job.fastp_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Fastp failed: {result.stderr}")
            job.status = "failed"
            job.save()
            return
        print(f"Fastp completed")
    except Exception as e:
        print(f"Fastp exception: {e}")
        job.status = "failed"
        job.save()
        return
    
    try:
        print(f"Running kraken2...")
        result = subprocess.run(job.kraken_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Kraken failed: {result.stderr}")
            job.status = "failed"
            job.save()
            return
        print(f"Kraken completed")
    except Exception as e:
        print(f"Kraken exception: {e}")
        job.status = "failed"
        job.save()
        return
    
    try:
        print(f"Running krona...")
        result = subprocess.run(job.krona_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Krona failed: {result.stderr}")
            job.status = "failed"
            job.save()
            return
        print(f"Krona completed")
    except Exception as e:
        print(f"Krona exception: {e}")
        job.status = "failed"
        job.save()
        return

    job.status = "completed"
    job.save()
    
    result = JobResult(job)
    result.save(job.filepath)
    print(f"Completed job {job.job_id} @ {time.ctime()}")


def cleanup_files(filepath):
    try:
        for file in os.listdir(filepath):
            if not file.endswith('_job.json'):
                file_path = os.path.join(filepath, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f'Error cleaning up files: {e}')


def main():
    print("Watching for jobs..")
    while True:
        try:
            for job_id in os.listdir(JOBS_DIR):
                job_dir = os.path.join(JOBS_DIR, job_id)
                if os.path.isdir(job_dir):
                    job_file = os.path.join(job_dir, f"{job_id}_job.json")
                    try:
                        job = load_job(job_file)
                        if job.status == "pending":
                            print(f"Processing job {job.job_id}...")
                            process_job(job)
                    except Exception as e:
                        print(f"Error in rading job file {job_file}: {e}")
        except Exception as e:
            print(f"Error scanning jobs directory: {e}")
        
        time.sleep(3)


def clean_unfinished_jobs():
    print("Cleaning up messeeeesss")
    try:
        for job_id in os.listdir(JOBS_DIR):
            job_dir = os.path.join(JOBS_DIR, job_id)
            if os.path.isdir(job_dir):
                job_file = os.path.join(job_dir, f"{job_id}_job.json")
                try:
                    job = load_job(job_file)
                    if job.status == "processing":
                        print(f"Cleaning up unfinished job {job.job_id}...")
                        job.status = "pending"
                        job.save()
                        cleanup_files(job.filepath)
                except Exception as e:
                    print(f"Error cleaning job {job_id}: {e}")
    except Exception as e:
        print(f"Error in cleanup handler: {e}")


atexit.register(clean_unfinished_jobs)

if __name__ == "__main__":
    main()
