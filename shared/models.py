"""Job class"""

import json


class Job:
    def __init__(
        self,
        job_id,
        fastq_filename_r1=None,
        fastq_filename_r2=None,
        filepath=None,
        status=None,
        fastp=None,
        kraken=None,
        fastq_filename=None,
        *args,
        **kwargs,
    ):
        self.job_id = job_id
        self.fastq_filename_r1 = fastq_filename_r1 or fastq_filename
        self.fastq_filename_r2 = fastq_filename_r2
        self.filepath = filepath
        self.status = status
        self.fastp = fastp
        self.kraken = kraken
        self.args = args
        self.kwargs = kwargs
        self.fastp_command = None
        self.kraken_command = None
        self.krona_command = None

    class FastP:
        def __init__(self, threads = 8, **kwargs):
            self.threads = threads
            self.quality = int(kwargs.get('min-quality'))
            self.trim_adapters = bool(kwargs.get('trim-adapters'))
            self.length_min = int(kwargs.get('length-min'))
            self.length_max = int(kwargs.get('length-max'))
            self.cut_front = bool(kwargs.get('cut-front'))
            self.cut_tail = bool(kwargs.get('cut-tail'))
            self.deduplicate = bool(kwargs.get('deduplicate'))
            self.paired = bool(kwargs.get('paired'))

    class Kraken:
        def __init__(self, db = "/human_viral_db", threads=8, **kwargs):
            self.db = db
            self.threads = threads
            self.confidence = float(kwargs.get('confidence'))
            self.paired_end = bool(kwargs.get('paired-end'))
            self.b_use_science_names = bool(kwargs.get('use-science-names'))
            self.base_quality = int(kwargs.get('base-quality'))
            self.use_science_names_str = "--use-names" if self.b_use_science_names else ""

    def create_commands(self):
        """Create cli commands for running fastp, kraken and krona with given configurations."""

        fastp_html_out = f"{self.filepath}/{self.job_id}_fastp.html"
        fastp_output_r1 = f"{self.filepath}/{self.job_id}_fastp_output.fastq"
        fastp_output_r2 = f"{self.filepath}/{self.job_id}_fastp_output_r2.fastq"
        kraken_report = f"{self.filepath}/{self.job_id}_kraken_report.txt"
        kraken_output = f"{self.filepath}/{self.job_id}_kraken_output.txt"
        krona_output = f"{self.filepath}/{self.job_id}_krona.html"

        trim_adapter_flag = "" if self.fastp.trim_adapters else "-A"
        cut_front_flag = "-5" if self.fastp.cut_front else ""
        cut_tail_flag = "-3" if self.fastp.cut_tail else ""
        dedup_flag = "--dedup" if self.fastp.deduplicate else ""

        is_paired = self.fastp.paired and self.fastq_filename_r2 != None

        if is_paired:
            self.fastp_command = (
                f"fastp -i {self.fastq_filename_r1} -I {self.fastq_filename_r2} "
                f"-h {fastp_html_out} -w {self.fastp.threads} -q {self.fastp.quality} "
                f"-l {self.fastp.length_min} --length_limit {self.fastp.length_max}"
                f" {trim_adapter_flag} {cut_front_flag} {cut_tail_flag} {dedup_flag} "
                f"-o {fastp_output_r1} -O {fastp_output_r2}"
            )
        else:
            self.fastp_command = (
                f"fastp -i {self.fastq_filename_r1} -h {fastp_html_out} "
                f"-w {self.fastp.threads} -q {self.fastp.quality} "
                f"-l {self.fastp.length_min} --length_limit {self.fastp.length_max}"
                f" {trim_adapter_flag} {cut_front_flag} {cut_tail_flag} {dedup_flag} "
                f"-o {fastp_output_r1}"
            )

        kraken_name_flag = f" {self.kraken.use_science_names_str}" if self.kraken.use_science_names_str else ""

        if is_paired:
            self.kraken_command = (
                f"kraken2 --db {self.kraken.db} --threads {self.kraken.threads} "
                f"--confidence {self.kraken.confidence} --minimum-base-quality {self.kraken.base_quality}"
                f"{kraken_name_flag} --paired --report {kraken_report} "
                f"--output {kraken_output} {fastp_output_r1} {fastp_output_r2}"
            )
        else:
            self.kraken_command = (
                f"kraken2 --db {self.kraken.db} --threads {self.kraken.threads} "
                f"--confidence {self.kraken.confidence} --minimum-base-quality {self.kraken.base_quality}"
                f"{kraken_name_flag} --report {kraken_report} "
                f"--output {kraken_output} {fastp_output_r1}"
            )

        self.krona_command = f"ktImportTaxonomy -o {krona_output} {kraken_report}"

    def save(self):
        """Save job info"""
        job_data = {
            "job_id": self.job_id,
            "fastq_filename": self.fastq_filename_r1,
            "fastq_filename_r1": self.fastq_filename_r1,
            "fastq_filename_r2": self.fastq_filename_r2,
            "filepath": self.filepath,
            "status": self.status,
            "fastp_command": self.fastp_command,
            "kraken_command": self.kraken_command,
            "krona_command": self.krona_command,
        }
        with open(f"{self.filepath}/{self.job_id}_job.json", "w") as f:
            json.dump(job_data, f, indent=4)
