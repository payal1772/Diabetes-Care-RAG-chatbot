function getStoredToken() {
    const token = localStorage.getItem("token");

    if (!token || token === "undefined" || token === "null" || token.split(".").length !== 3) {
        localStorage.removeItem("token");
        localStorage.removeItem("name");
        return null;
    }

    return token;
}

const token = getStoredToken();

if (!token) {
    window.location.href = "login.html";
}

async function readJsonResponse(response) {
    const text = await response.text();

    if (!text) {
        return {};
    }

    try {
        return JSON.parse(text);
    } catch (error) {
        throw new Error(`Backend returned a non-JSON response with status ${response.status}`);
    }
}

function asNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
}

function average(values) {
    const validValues = values.filter(value => value !== null);
    if (validValues.length === 0) return null;

    return validValues.reduce((total, value) => total + value, 0) / validValues.length;
}

function sum(values) {
    return values
        .filter(value => value !== null)
        .reduce((total, value) => total + value, 0);
}

function formatMetric(value, decimals = 0) {
    if (value === null || value === undefined) return "--";
    return Number(value).toFixed(decimals);
}

function renderMetricCards(logs) {
    const latest = logs[logs.length - 1] || {};
    const sleepValues = logs.map(item => asNumber(item.sleep));
    const waterValues = logs.map(item => asNumber(item.water));

    document.getElementById("latestGlucose").innerText = formatMetric(asNumber(latest.glucose));
    document.getElementById("avgSleep").innerText = formatMetric(average(sleepValues), 1);
    document.getElementById("totalWater").innerText = formatMetric(sum(waterValues));
    document.getElementById("latestSteps").innerText = formatMetric(asNumber(latest.steps));
}

function renderGlucoseChart(logs) {
    const times = logs.map(item => item.time);
    const glucoseValues = logs.map(item => asNumber(item.glucose));

    const chart = echarts.init(document.getElementById("glucoseChart"));

    chart.setOption({
        title: {
            text: "Glucose Trend",
            textStyle: {
                color: "#182026",
                fontSize: 18
            }
        },
        tooltip: {
            trigger: "axis"
        },
        grid: {
            top: 58,
            right: 24,
            bottom: 42,
            left: 54
        },
        xAxis: {
            type: "category",
            data: times,
            axisLabel: {
                interval: "auto",
                color: "#65727c"
            },
            axisTick: {
                show: false
            }
        },
        yAxis: {
            type: "value",
            name: "mg/dL",
            splitNumber: 4,
            axisLabel: {
                color: "#65727c"
            },
            splitLine: {
                lineStyle: {
                    color: "#edf1f3"
                }
            }
        },
        series: [
            {
                name: "Glucose",
                type: "line",
                data: glucoseValues,
                smooth: true,
                lineStyle: {
                    width: 3,
                    color: "#176b87"
                },
                itemStyle: {
                    color: "#176b87"
                }
            }
        ]
    });

    return chart;
}

function renderSmallTrendChart(logs, elementId, title, seriesName, values, color, unit, chartType = "line") {
    const times = logs.map(item => item.time);
    const chart = echarts.init(document.getElementById(elementId));

    chart.setOption({
        title: {
            text: title,
            textStyle: {
                color: "#182026",
                fontSize: 15
            }
        },
        tooltip: {
            trigger: "axis",
            valueFormatter: value => `${value} ${unit}`
        },
        grid: {
            top: 48,
            right: 14,
            bottom: 28,
            left: 38
        },
        xAxis: {
            type: "category",
            data: times,
            axisLabel: {
                interval: Math.max(0, Math.ceil(times.length / 3) - 1),
                color: "#65727c"
            },
            axisTick: {
                show: false
            }
        },
        yAxis: {
            type: "value",
            splitNumber: 3,
            axisLabel: {
                color: "#65727c"
            },
            splitLine: {
                lineStyle: {
                    color: "#edf1f3"
                }
            }
        },
        series: [
            {
                name: seriesName,
                type: chartType,
                data: values,
                smooth: chartType === "line",
                barMaxWidth: 34,
                lineStyle: {
                    width: 3,
                    color: color
                },
                itemStyle: {
                    color: color
                },
                areaStyle: chartType === "line" ? {
                    color: color,
                    opacity: 0.08
                } : undefined,
                symbolSize: 6,
                emphasis: {
                    focus: "series"
                }
            }
        ]
    });

    return chart;
}

function renderLifestyleCharts(logs) {
    return [
        renderSmallTrendChart(
            logs,
            "sleepChart",
            "Sleep Trend",
            "Sleep",
            logs.map(item => asNumber(item.sleep)),
            "#5b8c5a",
            "hours"
        ),
        renderSmallTrendChart(
            logs,
            "waterChart",
            "Water Intake Trend",
            "Water",
            logs.map(item => asNumber(item.water)),
            "#4d8fba",
            "glasses",
            "bar"
        ),
        renderSmallTrendChart(
            logs,
            "stepsChart",
            "Steps Trend",
            "Steps",
            logs.map(item => asNumber(item.steps)),
            "#d96c4a",
            "steps"
        )
    ];
}

function renderRecentLogs(logs) {
    const tbody = document.getElementById("recentLogs");
    tbody.innerHTML = "";

    logs.slice(-10).reverse().forEach(item => {
        const row = document.createElement("tr");
        const cells = [
            item.time || "--",
            formatMetric(asNumber(item.glucose)),
            item.meal || "--",
            formatMetric(asNumber(item.sleep), 1),
            formatMetric(asNumber(item.water)),
            formatMetric(asNumber(item.steps)),
            item.symptoms || "--"
        ];

        cells.forEach(cellText => {
            const cell = document.createElement("td");
            cell.innerText = cellText;
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });
}

async function loadDashboard() {
    try {
        const res = await fetch("/api/dashboard", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await readJsonResponse(res);

        if (res.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("name");
            window.location.href = "login.html";
            return;
        }

        if (!res.ok) {
            throw new Error(data.error || "Dashboard request failed");
        }

        const logs = data.glucose_logs || [];

        renderMetricCards(logs);
        const charts = [
            renderGlucoseChart(logs),
            ...renderLifestyleCharts(logs)
        ];
        renderRecentLogs(logs);

        window.addEventListener("resize", () => {
            charts.forEach(chart => chart.resize());
        });
    } catch (error) {
        console.error(error);
    }
}

if (token) {
    loadDashboard();
}
async function loadAnalytics() {
    try {
        const res = await fetch("/api/analytics", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await readJsonResponse(res);

        if (res.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("name");
            window.location.href = "login.html";
            return;
        }

        if (!res.ok) {
            throw new Error(data.error || "Analytics request failed");
        }

        document.getElementById("avgGlucose").innerText = data.average_glucose + " mg/dL";
        document.getElementById("highestGlucose").innerText = data.highest_glucose + " mg/dL";
        document.getElementById("timeInRange").innerText = data.time_in_range + "%";
        document.getElementById("riskyMeal").innerText = data.risky_meal;
        document.getElementById("lowSleepGlucose").innerText = data.low_sleep_high_glucose + " mg/dL";
    } catch (error) {
        console.error(error);
    }
}
loadAnalytics();
