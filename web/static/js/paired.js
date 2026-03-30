document.addEventListener("DOMContentLoaded", () => {
    const read2Label = document.getElementById("read2-label");
    const fastpPaired = document.getElementById("fastp-paired-select");
    const krakenPaired = document.getElementById("kraken-paired");

    const syncPairedState = (value, source) => {
        const showRead2 = value === "1";
        read2Label.style.display = showRead2 ? "inline" : "none";

        if (source === "kraken") {
            fastpPaired.value = value;
        }
        if (source === "fastp") {
            krakenPaired.value = value;
        }
    };

    fastpPaired.addEventListener("change", (event) => {
        syncPairedState(event.target.value, "fastp");
    });

    krakenPaired.addEventListener("change", (event) => {
        syncPairedState(event.target.value, "kraken");
    });
});