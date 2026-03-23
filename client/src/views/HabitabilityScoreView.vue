<template>
    <AppLayout>
        <div class="comparison-page">
            <section class="page-header">
                <h1>Habitability Score Comparison</h1>
                <p class="subtitle">Compare two postcodes across grouped habitability metrics.</p>
            </section>

            <section class="comparison-controls">
                <div class="controls-grid">
                    <div class="input-column">
                        <label for="left-postcode">Left Postcode</label>
                        <input
                            id="left-postcode"
                            v-model="leftPostcode"
                            type="text"
                            placeholder="e.g. CO7 0SH"
                            :disabled="loading"
                        />
                        <p v-if="leftError" class="error-text">{{ leftError }}</p>
                    </div>

                    <div class="compare-column">
                        <button class="compare-btn" @click="comparePostcodes" :disabled="loading || !canCompare">
                            {{ loading ? "Comparing..." : "Compare" }}
                        </button>
                    </div>

                    <div class="input-column">
                        <label for="right-postcode">Right Postcode</label>
                        <input
                            id="right-postcode"
                            v-model="rightPostcode"
                            type="text"
                            placeholder="e.g. DE56 4BG"
                            :disabled="loading"
                        />
                        <p v-if="rightError" class="error-text">{{ rightError }}</p>
                    </div>
                </div>
            </section>

            <section v-if="hasAnyResult" class="comparison-results">
                <div class="results-header">
                    <div class="postcode-pill">{{ leftResult?.postcode || normalizedLeft || "Left postcode" }}</div>
                    <div class="metric-heading">Metric</div>
                    <div class="postcode-pill">{{ rightResult?.postcode || normalizedRight || "Right postcode" }}</div>
                </div>

                <div
                    v-for="group in groupedMetrics"
                    :key="group.title"
                    class="metric-group"
                >
                    <h3>{{ group.title }}</h3>

                    <div
                        v-for="metric in group.metrics"
                        :key="metric.key"
                        class="metric-row"
                    >
                        <div class="value-cell left-value">{{ formatValue(leftResult?.[metric.key]) }}</div>
                        <div class="indicator-cell" :class="indicatorClass(metric)">
                            <span class="indicator-label">{{ getIndicatorLabel(metric) }}</span>
                        </div>
                        <div class="value-cell right-value">{{ formatValue(rightResult?.[metric.key]) }}</div>
                    </div>
                </div>
            </section>

            <section v-else-if="attemptedCompare" class="empty-state">
                <p>No score data available yet. Try different postcodes.</p>
            </section>
        </div>
    </AppLayout>
</template>

<script setup>
import { computed, ref } from "vue"
import AppLayout from "../components/AppLayout.vue"
import api from "../services/api"

const leftPostcode = ref("")
const rightPostcode = ref("")

const normalizedLeft = ref("")
const normalizedRight = ref("")

const leftResult = ref(null)
const rightResult = ref(null)

const leftError = ref("")
const rightError = ref("")

const loading = ref(false)
const attemptedCompare = ref(false)

const metricGroups = [
    {
        title: "Economy Metrics",
        metrics: [
            { key: "employmentRate", label: "Employment Rate", higherIsBetter: true },
            { key: "income", label: "Income", higherIsBetter: true },
            { key: "inflation", label: "Inflation", higherIsBetter: false },
        ],
    },
    {
        title: "Environment Metrics",
        metrics: [
            { key: "airQuality", label: "Air Quality", higherIsBetter: true },
            { key: "waterQuality", label: "Water Quality", higherIsBetter: true },
            { key: "landFertility", label: "Land Fertility", higherIsBetter: true },
            { key: "wasteManagement", label: "Waste Management", higherIsBetter: true },
        ],
    },
    {
        title: "Infrastructure Metrics",
        metrics: [
            { key: "education", label: "Education", higherIsBetter: true },
            { key: "healthcare", label: "Healthcare", higherIsBetter: true },
            { key: "transportation", label: "Transportation", higherIsBetter: true },
        ],
    },
    {
        title: "Security Metrics",
        metrics: [
            { key: "crime", label: "Crime", higherIsBetter: false },
            { key: "politics", label: "Politics", higherIsBetter: true },
            { key: "disasterRisks", label: "Disaster Risks", higherIsBetter: false },
            { key: "civicEngagement", label: "Civic Engagement", higherIsBetter: true },
        ],
    },
    {
        title: "Computed Scores",
        metrics: [
            { key: "economyScore", label: "Economy Score", higherIsBetter: true },
            { key: "environmentScore", label: "Environment Score", higherIsBetter: true },
            { key: "infrastructureScore", label: "Infrastructure Score", higherIsBetter: true },
            { key: "securityScore", label: "Security Score", higherIsBetter: true },
            { key: "overallScore", label: "Overall Score", higherIsBetter: true },
        ],
    },
]

const groupedMetrics = computed(() => metricGroups)

const hasAnyResult = computed(() => Boolean(leftResult.value || rightResult.value))

const canCompare = computed(() =>
    leftPostcode.value.trim().length > 0 && rightPostcode.value.trim().length > 0,
)

function normalizePostcode(postcode) {
    return postcode.trim().toUpperCase()
}

function extractErrorMessage(error) {
    if (error?.response?.data?.message) {
        return error.response.data.message
    }
    if (error?.response?.status) {
        return `Request failed (${error.response.status})`
    }
    return "Unable to fetch habitability score"
}

function asNumber(value) {
    return typeof value === "number" && Number.isFinite(value) ? value : null
}

function formatValue(value) {
    const n = asNumber(value)
    if (n === null) {
        return "--"
    }
    return Number.isInteger(n) ? String(n) : n.toFixed(2)
}

function compareMetric(metric, leftValue, rightValue) {
    const left = asNumber(leftValue)
    const right = asNumber(rightValue)
    if (left === null || right === null) {
        return "none"
    }

    const delta = left - right
    if (Math.abs(delta) < 0.0001) {
        return "equal"
    }

    const leftBetter = metric.higherIsBetter ? delta > 0 : delta < 0
    return leftBetter ? "left" : "right"
}

function getIndicatorLabel(metric) {
    const outcome = compareMetric(metric, leftResult.value?.[metric.key], rightResult.value?.[metric.key])
    if (outcome === "left") {
        return `< ${metric.label}`
    }
    if (outcome === "right") {
        return `${metric.label} >`
    }
    if (outcome === "equal") {
        return `= ${metric.label} =`
    }
    return metric.label
}

function indicatorClass(metric) {
    const outcome = compareMetric(metric, leftResult.value?.[metric.key], rightResult.value?.[metric.key])
    return {
        "winner-left": outcome === "left",
        "winner-right": outcome === "right",
        "winner-equal": outcome === "equal",
    }
}

async function comparePostcodes() {
    attemptedCompare.value = true
    leftError.value = ""
    rightError.value = ""
    leftResult.value = null
    rightResult.value = null

    normalizedLeft.value = normalizePostcode(leftPostcode.value)
    normalizedRight.value = normalizePostcode(rightPostcode.value)

    if (!normalizedLeft.value || !normalizedRight.value) {
        if (!normalizedLeft.value) {
            leftError.value = "Please enter a postcode"
        }
        if (!normalizedRight.value) {
            rightError.value = "Please enter a postcode"
        }
        return
    }

    loading.value = true

    const [leftResponse, rightResponse] = await Promise.allSettled([
        api.get(`/habitability/${encodeURIComponent(normalizedLeft.value)}`),
        api.get(`/habitability/${encodeURIComponent(normalizedRight.value)}`),
    ])

    if (leftResponse.status === "fulfilled") {
        leftResult.value = leftResponse.value.data
    } else {
        leftError.value = extractErrorMessage(leftResponse.reason)
    }

    if (rightResponse.status === "fulfilled") {
        rightResult.value = rightResponse.value.data
    } else {
        rightError.value = extractErrorMessage(rightResponse.reason)
    }

    loading.value = false
}
</script>

<style scoped>
.comparison-page {
    min-height: 100vh;
    background: #f8fafc;
    padding: 36px 26px 60px;
}

.page-header {
    text-align: center;
    margin-bottom: 26px;
}

.page-header h1 {
    margin: 0;
    color: #1e293b;
    font-size: 2rem;
}

.subtitle {
    margin-top: 10px;
    color: #475569;
}

.comparison-controls {
    max-width: 1100px;
    margin: 0 auto 24px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    padding: 20px;
}

.controls-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 16px;
    align-items: center;
}

.input-column {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.input-column label {
    color: #334155;
    font-weight: 600;
}

.input-column input {
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 12px 14px;
    font-size: 1rem;
}

.input-column input:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.compare-column {
    display: flex;
    justify-content: center;
}

.compare-btn {
    border: none;
    background: #1e40af;
    color: white;
    padding: 12px 24px;
    border-radius: 9999px;
    font-weight: 700;
    cursor: pointer;
}

.compare-btn:disabled {
    cursor: not-allowed;
    opacity: 0.65;
}

.error-text {
    margin: 0;
    color: #b91c1c;
    font-size: 0.9rem;
}

.comparison-results {
    max-width: 1100px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    padding: 22px;
}

.results-header {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
    align-items: center;
}

.postcode-pill {
    text-align: center;
    border-radius: 9999px;
    padding: 10px 14px;
    background: #eff6ff;
    color: #1d4ed8;
    font-weight: 700;
}

.metric-heading {
    text-align: center;
    color: #334155;
    font-weight: 700;
}

.metric-group {
    border-top: 1px solid #e2e8f0;
    padding-top: 16px;
    margin-top: 16px;
}

.metric-group h3 {
    margin: 0 0 10px;
    color: #0f172a;
    font-size: 1rem;
}

.metric-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    align-items: center;
    padding: 8px 0;
}

.value-cell {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    min-height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #1e293b;
}

.indicator-cell {
    min-height: 42px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #475569;
    background: #ffffff;
}

.indicator-label {
    font-size: 1rem;
    font-weight: 700;
}

.winner-left {
    background: #eff6ff;
    border-color: #bfdbfe;
    color: #1e40af;
}

.winner-right {
    background: #eff6ff;
    border-color: #bfdbfe;
    color: #1e40af;
}

.winner-equal {
    background: #f1f5f9;
    color: #334155;
}

.empty-state {
    max-width: 1100px;
    margin: 0 auto;
    text-align: center;
    color: #475569;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
}

@media (max-width: 900px) {
    .controls-grid {
        grid-template-columns: 1fr;
    }

    .compare-column {
        order: 3;
    }
}

@media (max-width: 720px) {
    .results-header {
        grid-template-columns: 1fr;
    }

    .metric-row {
        grid-template-columns: 1fr;
    }
}
</style>
