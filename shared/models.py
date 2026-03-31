"""Datamodel voor pipeline jobs en command opbouw."""

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
        """Maak een Job object met paden, status en configuratie.

        Input:
            job_id: id van de job.
            fastq_filename_r1: Pad naar FASTQ read 1.
            fastq_filename_r2: Pad naar FASTQ read 2 of None.
            filepath: Map van de job in /data.
            status: jobstatus.
            fastp: FastP configuratie.
            kraken: Kraken configuratie.
        """
        self.job_id = job_id
        self.fastq_filename_r1 = fastq_filename_r1
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
        self.job_size = None

        self.fastp_html_out = f"{self.filepath}/{self.job_id}_fastp.html"
        self.fastp_output_r1 = f"{self.filepath}/{self.job_id}_fastp_output.fastq"
        self.fastp_output_r2 = f"{self.filepath}/{self.job_id}_fastp_output_r2.fastq"
        self.kraken_report = f"{self.filepath}/{self.job_id}_kraken_report.txt"
        self.kraken_output = f"{self.filepath}/{self.job_id}_kraken_output.txt"
        self.krona_output = f"{self.filepath}/{self.job_id}_krona.html"

    class FastP:
        def __init__(self, threads=8, **kwargs):
            """Zet fastp instellingen om naar variabelen.

            Input:
                threads: Aantal threads voor fastp.
                kwargs: Waarden uit formulier zoals quality en cut flags.
            """
            self.threads = threads
            self.quality = kwargs.get('min-quality')
            self.trim_adapters = kwargs.get('trim-adapters')
            self.length_min = kwargs.get('length-min')
            self.length_max = kwargs.get('length-max')
            self.cut_front = kwargs.get('cut-front')
            self.cut_tail = kwargs.get('cut-tail')
            self.deduplicate = kwargs.get('deduplicate')
            self.paired = kwargs.get('paired')

    class Kraken:
        def __init__(self, db="/human_viral_db", threads=8, **kwargs):
            """Zet kraken instellingen om naar variabelen.

            Input:
                db: Pad naar de kraken database.
                threads: Aantal threads voor kraken.
                kwargs: Waarden uit formulier zoals confidence.
            """
            self.db = db
            self.threads = threads
            self.confidence = kwargs.get('confidence')
            self.paired_end = kwargs.get('paired-end')
            self.b_use_science_names = kwargs.get('use-science-names')
            self.base_quality = kwargs.get('base-quality')
            self.use_science_names_str = "--use-names" if self.b_use_science_names else ""

    def create_commands(self):
        """Maak de shell commands voor fastp, kraken2 en krona.

        Input:
            Gebruikt variabelen uit self.fastp, self.kraken en job paden.
        """

        trim_adapter_flag = "" if self.fastp.trim_adapters else "-A"
        cut_front_flag = "-5" if self.fastp.cut_front else ""
        cut_tail_flag = "-3" if self.fastp.cut_tail else ""
        dedup_flag = "--dedup" if self.fastp.deduplicate else ""

        # Alleen paired-end als de optie aan staat en read 2 er is.
        is_paired = self.fastp.paired and self.fastq_filename_r2 != None

        if is_paired:
            self.fastp_command = (
                f"fastp -i {self.fastq_filename_r1} -I {self.fastq_filename_r2} "
                f"-h {self.fastp_html_out} -w {self.fastp.threads} -q {self.fastp.quality} "
                f"-l {self.fastp.length_min} --length_limit {self.fastp.length_max}"
                f" {trim_adapter_flag} {cut_front_flag} {cut_tail_flag} {dedup_flag} "
                f"-o {self.fastp_output_r1} -O {self.fastp_output_r2}"
            )
        else:
            self.fastp_command = (
                f"fastp -i {self.fastq_filename_r1} -h {self.fastp_html_out} "
                f"-w {self.fastp.threads} -q {self.fastp.quality} "
                f"-l {self.fastp.length_min} --length_limit {self.fastp.length_max}"
                f" {trim_adapter_flag} {cut_front_flag} {cut_tail_flag} {dedup_flag} "
                f"-o {self.fastp_output_r1}"
            )

        # Voeg de --use-names vlag alleen toe als het gekozen is op de website.
        kraken_name_flag = f" {self.kraken.use_science_names_str}" if self.kraken.use_science_names_str else ""

        if is_paired:
            self.kraken_command = (
                f"kraken2 --db {self.kraken.db} --threads {self.kraken.threads} "
                f"--confidence {self.kraken.confidence} --minimum-base-quality {self.kraken.base_quality}"
                f"{kraken_name_flag} --paired --report {self.kraken_report} "
                f"--output {self.kraken_output} {self.fastp_output_r1} {self.fastp_output_r2}"
            )
        else:
            self.kraken_command = (
                f"kraken2 --db {self.kraken.db} --threads {self.kraken.threads} "
                f"--confidence {self.kraken.confidence} --minimum-base-quality {self.kraken.base_quality}"
                f"{kraken_name_flag} --report {self.kraken_report} "
                f"--output {self.kraken_output} {self.fastp_output_r1}"
            )

        self.krona_command = f"ktImportTaxonomy -m 3 -t 5 -o {self.krona_output} {self.kraken_report}"

    def save(self):
        """Sla job informatie op als JSON bestand in de job map.

        Input:
            Gebruikt alle self variabelen.
        """
        is_paired = self.fastq_filename_r2 and getattr(self.fastp, "paired", True)

        job_data = {
            "job_id": self.job_id,
            "fastq_filename_r1": self.fastq_filename_r1,
            "fastq_filename_r2": self.fastq_filename_r2,
            "filepath": self.filepath,
            "status": self.status,
            "fastp_command": self.fastp_command,
            "kraken_command": self.kraken_command,
            "krona_command": self.krona_command,
            "job_size": self.job_size,
            "rm_after_fastp": [self.fastq_filename_r1, self.fastq_filename_r2] if is_paired else [self.fastq_filename_r1],
            "rm_after_kraken": [self.fastp_output_r1, self.fastp_output_r2] if is_paired else [self.fastp_output_r1],
            "rm_after_krona": [self.kraken_output],
        }
        with open(f"{self.filepath}/{self.job_id}_job.json", "w") as f:
            json.dump(job_data, f, indent=4)
