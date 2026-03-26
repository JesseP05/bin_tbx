document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("fastp-paired-select").addEventListener("change", function() {
        input_r2 = document.getElementById("read2-label");
        kraken_paired = document.getElementById("kraken-paired");
        if (this.value === "1") {
            input_r2.style.display = "inline";
            kraken_paired.value = "1";
        } else {
            input_r2.style.display = "none";
            kraken_paired.value = "0";
            kraken_paired.dispatchEvent(new Event("change"));
        }
    });
    document.getElementById("kraken-paired").addEventListener("change", function() {
        input_r2 = document.getElementById("read2-label");
        fast_paired = document.getElementById("fastp-paired-select");
        if (this.value === "1") {
            input_r2.style.display = "inline";
            fast_paired.value = "1";
        } else {
            input_r2.style.display = "none";
            fast_paired.value = "0";
            fast_paired.dispatchEvent(new Event("change"));
        }
    });
});