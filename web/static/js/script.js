document.addEventListener('DOMContentLoaded', () => {
    const resultGrid = document.querySelector('[data-job-id]');
    if (!resultGrid) {
        console.log("No id given, no job started this session.");
        return;
    }
    const jobId = resultGrid.dataset.jobId;
    if (jobId && jobId !== 'None') {
        document.getElementById("throbber").style.display = "block";
        fetchTimeout = setTimeout(() => getJobStatus(jobId), 4000);
    }
    
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', () => {
            document.getElementById("throbber").style.display = "block";
            document.getElementById("results-container").style.display = "none";
        });
    }
});

function getJobStatus(id) {
    fetch(`/job/${id}/status`)
        .then(res => res.json())
        .then(data => {
            if (data.status === "completed") {
		if (fetchTimeout){
			clearTimeout(fetchTimeout);
			fetchTimeout = null;
		}
		showResults(data)
            } else if (data.status === "processing" || data.status === "pending") {
                fetchTimeout = setTimeout(() => getJobStatus(id), 2000);
            }
        })
        .catch(err => console.error("Error polling status:", err));
}

function showResults(data) {
    document.getElementById("throbber").style.display = "none";
    
    if (data.fastq_report && data.krona_output) {
        document.getElementById("fastp-result").src = "../" + data.fastq_report;
        document.getElementById("kraken-result").src = "../" + data.krona_output;
        document.getElementById("results-container").style.display = "block";
    }
}
