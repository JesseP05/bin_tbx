document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme-preference");
    if (savedTheme == "dark") {
        document.documentElement.setAttribute("data-theme", "dark");
        document.getElementById("theme-toggle").textContent = "☀️";
    }

    document.getElementById("theme-toggle")?.addEventListener("click", () => {
        const html = document.documentElement;
        if (html.getAttribute("data-theme") == "dark") {
            html.removeAttribute("data-theme");
            document.getElementById("theme-toggle").textContent = "🌙";
            localStorage.setItem("theme-preference", "light");
        } else {
            html.setAttribute("data-theme", "dark");
            document.getElementById("theme-toggle").textContent = "☀️";
            localStorage.setItem("theme-preference", "dark");
        }
    });

    const resultGrid = document.querySelector("[data-job-id]");
    if (!resultGrid) {
        console.log("No id given, no job started this session.");
        return;
    }
    const jobId = resultGrid.dataset.jobId;
    if (jobId && jobId !== "None") {
        document.getElementById("submit_btn").style.display = "none";
        document.getElementById("throbber").style.display = "block";
        fetchTimeout = setTimeout(() => getJobStatus(jobId), 10000);
    }
    
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", () => {
            document.getElementById("throbber").style.display = "block";
            document.getElementById("submit_btn").style.display = "none";
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
                fetchTimeout = setTimeout(() => getJobStatus(id), 10000);
            }
        })
        .catch(err => console.error("Error polling status:", err));
}

function showResults(data) {
    document.getElementById("throbber").style.display = "none";
    
    if (data.fastq_report && data.krona_output) {
        document.getElementById("fastp-result").src = "../" + data.fastq_report;
        document.getElementById("kraken-result").src = "../" + data.krona_output;
        document.getElementById("new-analysis").style.display = "inline-block";
        document.getElementById("results-container").style.display = "block";
    }
}
