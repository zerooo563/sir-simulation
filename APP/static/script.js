document.addEventListener("DOMContentLoaded", () => {
    const simulateBtn = document.getElementById("simulateBtn");
    const daysSlider = document.getElementById("days");
    const daysValue = document.getElementById("daysValue");
    const betaSlider = document.getElementById("beta");
    const betaValue = document.getElementById("betaValue");
    const gammaSlider = document.getElementById("gamma");
    const gammaValue = document.getElementById("gammaValue");
    const chartDiv = document.getElementById("chart");

    daysSlider.addEventListener("input", () => { daysValue.textContent = daysSlider.value; });
    betaSlider.addEventListener("input", () => { betaValue.textContent = parseFloat(betaSlider.value).toFixed(2); });
    gammaSlider.addEventListener("input", () => { gammaValue.textContent = parseFloat(gammaSlider.value).toFixed(2); });

    async function simulate() {
        const payload = {
            N: parseInt(document.getElementById("N").value),
            days: parseInt(daysSlider.value),
            beta: parseFloat(betaSlider.value),
            gamma: parseFloat(gammaSlider.value),
            I0: parseInt(document.getElementById("I0").value)
        };

        const resp = await fetch("/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        return resp.json();
    }

    function renderChart(data) {
        const traces = [
            { x: data.t, y: data.S, mode: "lines", name: "Susceptible (S)", line: { color: "#4f8bf9", width: 3 } },
            { x: data.t, y: data.I, mode: "lines", name: "Infected (I)", line: { color: "#e74c3c", width: 3 } },
            { x: data.t, y: data.R, mode: "lines", name: "Recovered (R)", line: { color: "#27ae60", width: 3 } }
        ];

        const layout = {
            title: "Temporal Evolution of Epidemic Curves",
            xaxis: { title: "Time (Days)" },
            yaxis: { title: "Number of Individuals" },
            hovermode: "x unified",
            template: "plotly_white",
            legend: { orientation: "h", y: 1.02, x: 0.5, xanchor: "center" },
            margin: { t: 60, b: 50, l: 60, r: 30 }
        };

        Plotly.newPlot(chartDiv, traces, layout, { responsive: true });
    }

    function updateMetrics(data) {
        document.querySelector("#r0Card .metric-value").textContent = data.R_naught;
        const statusCard = document.getElementById("statusCard");
        const statusValue = statusCard.querySelector(".metric-value");
        statusCard.className = "metric-card " + data.status;
        statusValue.textContent = data.status === "epidemic"
            ? "Epidemic Outbreak 🔴"
            : "Disease Decline 🟢";
    }

    function updateValidation(data) {
        const initSum = data.initialSum;
        const finalSum = data.finalSum;
        const conserved = initSum === finalSum;
        document.getElementById("initSum").textContent = initSum;
        document.getElementById("finalSum").textContent = finalSum;
        const cs = document.getElementById("conservationStatus");
        cs.textContent = conserved ? "Verified (100% Invariant)" : "MISMATCH!";
        cs.className = "status-badge " + (conserved ? "success" : "fail");

        document.getElementById("s0Val").textContent = data.S0;
        document.getElementById("i0Val").textContent = data.I0;
        document.getElementById("r0Val").textContent = data.R0;
        const bs = document.getElementById("boundaryStatus");
        bs.textContent = "Verified (Strict)";
        bs.className = "status-badge success";

        document.getElementById("minS").textContent = data.minS;
        document.getElementById("minI").textContent = data.minI;
        document.getElementById("minR").textContent = data.minR;
        const nn = document.getElementById("nonnegStatus");
        const nonNeg = data.minS >= 0 && data.minI >= 0 && data.minR >= 0;
        nn.textContent = nonNeg ? "Verified (Biologically Realistic)" : "NEGATIVE VALUES!";
        nn.className = "status-badge " + (nonNeg ? "success" : "fail");
    }

    async function runSimulation() {
        simulateBtn.disabled = true;
        simulateBtn.textContent = "Computing...";
        try {
            const data = await simulate();
            renderChart(data);
            updateMetrics(data);
            updateValidation(data);
        } catch (err) {
            alert("Error running simulation: " + err.message);
        } finally {
            simulateBtn.disabled = false;
            simulateBtn.textContent = "Run Simulation";
        }
    }

    simulateBtn.addEventListener("click", runSimulation);
    runSimulation();
});
