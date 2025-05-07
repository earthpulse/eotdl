<script>
    import { PUBLIC_AI4EO_API } from "$env/static/public";
    import { onMount } from "svelte";

    let { dataset } = $props();

    let leaderboard = $state([]);
    let loading = $state(true);
    let mode = $derived(dataset.benchmark.mode);
    let chartElement;
    let chart;

    $effect(async () => {
        loading = true;
        const res = await fetch(
            `${PUBLIC_AI4EO_API}/leaderboard/${dataset.benchmark.challenge}`,
        );
        if (res.ok) {
            const data = await res.json();
            leaderboard = data.map((item) => ({
                team: item.team.name,
                metric: item.metrics[dataset.benchmark.metric].public,
            }));

            // Sort leaderboard by metric value (assuming higher is better)
            if (mode === "max") {
                leaderboard.sort((a, b) => a.metric - b.metric);
            } else {
                leaderboard.sort((a, b) => b.metric - a.metric);
            }

            if (leaderboard.length > 0) {
                // Create chart on next tick to ensure DOM is ready
                setTimeout(createChart, 0);
            }
        }
        loading = false;
        return () => {
            if (chart) chart.destroy();
        };
    });

    function createChart() {
        if (!chartElement || leaderboard.length === 0) return;

        // Dynamically import Chart.js
        import("chart.js/auto")
            .then((ChartModule) => {
                const Chart = ChartModule.default;

                // Destroy previous chart if it exists
                if (chart) chart.destroy();

                // Create the chart
                chart = new Chart(chartElement, {
                    type: "line",
                    data: {
                        labels: leaderboard.map((item) => item.team),
                        datasets: [
                            {
                                label: dataset.benchmark.metric,
                                data: leaderboard.map((item) => item.metric),
                                backgroundColor: "rgba(75, 192, 192, 0.7)",
                                borderColor: "rgba(75, 192, 192, 1)",
                                borderWidth: 2,
                                pointBackgroundColor: "rgba(75, 192, 192, 1)",
                                pointBorderColor: "#fff",
                                pointRadius: 6,
                                pointHoverRadius: 8,
                                fill: false,
                                tension: 0.3,
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: "Benchmark",
                                font: {
                                    size: 16,
                                },
                            },
                            legend: {
                                display: false,
                            },
                            tooltip: {
                                callbacks: {
                                    title: (context) =>
                                        `Team: ${context[0].label}`,
                                    label: (context) =>
                                        `${dataset.benchmark.metric}: ${context.formattedValue}`,
                                },
                            },
                        },
                        scales: {
                            y: {
                                title: {
                                    display: true,
                                    text: "Score",
                                },
                                beginAtZero: mode === "min" ? true : false,
                            },
                            x: {
                                title: {
                                    display: false,
                                },
                                ticks: {
                                    font: {
                                        size: 11,
                                    },
                                    autoSkip: true,
                                    maxRotation: 90,
                                    minRotation: 45,
                                },
                            },
                        },
                        layout: {
                            padding: {
                                bottom: 6,
                            },
                        },
                    },
                });
            })
            .catch((error) => {
                console.error("Error loading Chart.js:", error);
            });
    }
</script>

{#if loading}
    <div>
        <p>Loading benchmark...</p>
    </div>
{:else if leaderboard.length > 0}
    <div class="benchmark-container">
        <div
            class="chart-container"
            style="position: relative; height: 300px; width: 100%;"
        >
            <canvas bind:this={chartElement}></canvas>
        </div>
    </div>
{:else}
    <p>Benchmark not available</p>
{/if}

<style>
    .benchmark-container {
        margin: 1rem 0;
        padding: 1rem 1rem 2rem 1rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        overflow-x: auto;
    }

    .chart-container {
        margin-top: 1rem;
        padding-bottom: 20px;
    }

    h2 {
        margin-top: 0;
    }
</style>
