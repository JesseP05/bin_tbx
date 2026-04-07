"""
    watcher.py
    Script that finds new/unfinished jobs and processes them by calling tools using subprocess.

"""


import json
import time
import os
import subprocess
import atexit
from shared.models import Job


JOBS_DIR = "/data"


class JobResult:
    """Class that encapsulates processed jobs results.
    args : 
    Takes in job instance and translates its properties to a new instance of JobResult.
    """
    def __init__(self, job):
        """Translate job to a jobresult file.
        args : 
        job : Instance of job class.
        """
        self.job_id = job.job_id
        self.status = "completed"
        self.fastq_report = f"{job.filepath}/{job.job_id}_fastp.html"
        self.fastp_output = f"{job.filepath}/{job.job_id}_fastp_output.fastq"
        self.kraken_report = f"{job.filepath}/{job.job_id}_kraken_report.txt"
        self.kraken_output = f"{job.filepath}/{job.job_id}_kraken_output.txt"
        self.krona_output = f"{job.filepath}/{job.job_id}_krona.html"
        self.completed_at = time.ctime()
        self.job_size = job.job_size
    
    def save(self, job_dir):
        """Save job result to file.
        args :
        job_dir : Location whree the job should be saved.
        """
        with open(f"{job_dir}/{self.job_id}_results.json", "w") as f:
            json.dump(self.__dict__, f, indent=4)

    def __str__(self):
        """return job id and status in string form"""
        job_string = f"{self.job_id} is: {self.status}"
        return job_string


def load_job(job_file):
    """Load job instance from saved json file
    args :
    job_file : location of the json file.
    
    returns : 
    job : instance of models.Job.
    """
    with open(job_file, "r") as f:
        data = json.load(f)
    job = Job(
        job_id=data["job_id"],
        fastq_filename_r1=data.get("fastq_filename_r1"),
        fastq_filename_r2=data.get("fastq_filename_r2"),
        filepath=data["filepath"],
        status=data["status"],
    )
    job.fastp_command = data.get("fastp_command")
    job.kraken_command = data.get("kraken_command")
    job.krona_command = data.get("krona_command")
    job.job_size = data.get("job_size")
    job.rm_after_fastp = data.get("rm_after_fastp") or []
    job.rm_after_kraken = data.get("rm_after_kraken") or []
    job.rm_after_krona = data.get("rm_after_krona") or []
    return job


def run_tool(job, tool, command):
    """runs tools with command line arguments
    args : 
    job : the current job instance.
    tool : current tool to run.
    command : the command that runs the tool with parameters.
    """
    try:
        print(f"Running {tool}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{tool} failed: {result.stderr}")
            job.status = "failed"
            job.save()
            return False
        print(f"{tool} completed")

        # remove large process files to save space
        match tool:
            case "fastp":
                for f in job.rm_after_fastp:
                    if f:
                        os.remove(f)
            case "kraken2":
                for f in job.rm_after_kraken:
                    if f:
                        os.remove(f)
            case "krona":
                for f in job.rm_after_krona:
                    if f:
                        os.remove(f)
        return True
    except Exception as e:
        print(f"{tool} exception: {e}")
        job.status = "failed"
        job.save()
        return False


def process_job(job):
    """function that handles proper job loading and saving.
    args : 
    job : instance of models.Job
    """
    job.status = "processing"
    job.save()

    tool_args = [
        ("fastp", job.fastp_command),
        ("kraken2", job.kraken_command),
        ("krona", job.krona_command)
    ]
    for tool, command in tool_args:
        if not run_tool(job, tool, command):
            return

    job.status = "completed"
    # get job directories filesize to show on history page
    result = subprocess.run(f"du -hs {job.filepath}", shell=True, stdout=subprocess.PIPE, text=True)
    job.job_size = result.stdout.strip().split()[0] if result.returncode == 0 else None
    job.save()
    
    result = JobResult(job)
    result.save(job.filepath)
    print(f"Completed job {job.job_id} @ {time.ctime()}")


def cleanup_files(filepath):
    """function that cleans up leftover/unfinished files on filepath
    args : 
    filepath : job directory path
    """
    try:
        for file in os.listdir(filepath):
            if not file.endswith('_job.json'):
                file_path = os.path.join(filepath, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f'Error cleaning up files: {e}')


def main():
    """function that handles main waiting loop and calls functions when necessary
    """
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
                        if job.status == 'downloading':
                            break
                        print(f"Error in reading job file {job_file}: {e}")
        except Exception as e:
            print(f"Error scanning jobs directory: {e}")
        
        time.sleep(3)


def clean_unfinished_jobs():
    """handles cleanup of unfinished jobs when shutdown is cutting off a process."""
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

# register function to run on shutdown
if os.getenv("IN_DOCKER"):
    atexit.register(clean_unfinished_jobs)

if __name__ == "__main__":
    main()
