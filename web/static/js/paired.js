document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("fastp-paired-select").addEventListener("change", function() {
        input_r2 = document.getElementById("read2-label");
        if (this.value === "true") {
            input_r2.style.display = "inline";
        } else {
            input_r2.style.display = "none";
        }
    });
});