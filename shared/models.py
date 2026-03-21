"""Job class"""

import json


class Job:
    def __init__(self, job_id, fastq_filename, filepath, status, fastp=None, kraken=None, *args, **kwargs):
        self.job_id = job_id
        self.fastq_filename = fastq_filename
        self.filepath = filepath
        self.status = status
        self.fastp = fastp
        self.kraken = kraken
        self.args = args
        self.kwargs = kwargs
        self.fastp_command = None
        self.kraken_command = None

    class FastP:
        def __init__(self, threads = 4, **kwargs):
            self.threads = threads
            self.quality = int(kwargs.get('min-quality'))
            self.trim_adapters = bool(kwargs.get('trim-adapters'))
            self.length_min = int(kwargs.get('length-min'))
            self.length_max = int(kwargs.get('length-max'))
            self.cut_front = bool(kwargs.get('cut-front'))
            self.cut_tail = bool(kwargs.get('cut-tail'))
            self.deduplicate = bool(kwargs.get('deduplicate'))
    
    class Kraken:
        def __init__(self, db = '/human_viral_db', threads = 4, **kwargs):
            self.db = db
            self.threads = threads
            self.confidence = float(kwargs.get('confidence'))
            self.paired_end = bool(kwargs.get('paired-end'))
            self.use_science_names = bool(kwargs.get('use-science-names'))
            self.base_quality = int(kwargs.get('base-quality'))
    
    def create_commands(self):
        """Create cli commands for running fastp and kraken2 with given configurations."""

        self.fastp_command = f"fastp -i {self.fastq_filename} -h {self.filepath}/{self.job_id}_fastp.html \
        -w {self.fastp.threads} -q {self.fastp.quality} -l {self.fastp.length_min} \
        --length_limit {self.fastp.length_max} -A {self.fastp.trim_adapters} \
        -5 {self.fastp.cut_front} -3 {self.fastp.cut_tail} --dedup {self.fastp.deduplicate} \
        -o {self.filepath}/{self.job_id}_fastp_output.fastq"
        
        self.kraken_command = f"kraken2 --db {self.kraken.db} --threads {self.kraken.threads} --confidence {self.kraken.confidence} \
        --use-names {self.kraken.use_science_names} --minimum-base-quality {self.kraken.base_quality} --report {self.filepath}/{self.job_id}_kraken_report.txt \
        --output {self.filepath}/{self.job_id}_kraken_output.txt {self.filepath}/{self.job_id}_fastp_output.fastq"


    def save(self):
        """Save job info"""
        job_data = {
            "job_id": self.job_id,
            "fastq_filename": self.fastq_filename,
            "filepath": self.filepath,
            "status": self.status,
            "fastp_command": self.fastp_command,
            "kraken_command": self.kraken_command,
        }
        with open(f"{self.filepath}/{self.job_id}_job.json", "w") as f:
            json.dump(job_data, f, indent=4)