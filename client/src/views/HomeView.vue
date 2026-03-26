<template>
    <AppLayout>
        <div class="home-page">
            <section class="hero">
                <div class="hero-content">
                    <h1>Know Your Area. <br>Protect your community.</h1>
                    <p class="subtitle">
                        Real-time habitability scores ~ Community reporting ~ 
                        Built for everyone (WCAG Level A compliant)
                    </p>
                    <div class="cta-buttons">
                        <button @click="goToHabitabilityView" class="btn-primary">
                            Check Habitability Score
                        </button>
                        <button @click="goToReports" class="btn-secondary">
                            Report an Issue Now
                        </button>
                    </div>
                </div>

                <div class="score-card">
                    <h3>West Midlands</h3>
                    <div class="score-circle">
                        <span class="score">74</span>
                        <span class="label">/100</span>
                    </div>
                    <p class="score-detail">Moderate ~ Stable ~ 3 active reports</p>
                </div>
            </section>

            <section class="features">
                <h2>Core Features</h2>
                <div class="features-grid">
                    <div class="feature-card" @click="goToHabitabilityView">
                        <h3>Habitability Overview</h3>
                        <p>Interactive visual comparison tool for habitability metrics, across any two areas of the country.</p>
                    </div>

                    <div class="feature-card" @click="goToReports">
                        <h3>Report Issues</h3>
                        <p>Map markers + searchable cards. Vote, track status (Pending/In Progress/Resolved).</p>
                    </div>

                    <div class="feature-card" @click="openAccessibility">
                        <h3>Accessibility Settings</h3>
                        <p>Colour-blind modes, dyslexic fonts (OpenDyslexic, Lexend), text size, keyboard navigation – persistent across the whole app.</p>
                    </div>
                </div>
            </section>

            <section class="recent-reports">
                <h2>Latest Community Reports</h2>
                <div class="reports-teaser">
                    <div v-for="(report, i) in recentReports" :key="i" class="teaser-card" @click="goToReports">
                        <span class="type" :style="{ backgroundColor: getIconColor(report.type) }">
                            {{ report.type }}
                        </span>
                        <span class="area">{{ report.area }}</span>
                        <span class="votes">{{ report.votes }} votes</span>
                    </div>
                </div>
                <button @click="goToReports" class="view-all-btn">View All Reports →</button>
            </section>
        </div>
    </AppLayout>
</template>

<script setup>
import AppLayout from "../components/AppLayout.vue"
import { ref, onMounted } from "vue"
import { useRouter } from 'vue-router'
import { useAccessibility } from "../composables/useAccessibility"

const recentReports = ref([])
const router = useRouter()
const { openAccessibility } = useAccessibility()

const API = `${import.meta.env.VITE_API_URL}/api/v1`
const NEIGHBOURHOOD_ID = 1

async function loadRecentReports() {
    try {
        const res = await fetch(`${API}/reports?neighbourhoodId=${NEIGHBOURHOOD_ID}`, {credentials: 'include'})
        if (!res.ok) throw new Error()
        let data = await res.json()
        recentReports.value = data.slice(0, 3).map(r => ({
            type: r.title || 'Community Report', 
            area: 'West Midlands', 
            votes: r.voteCount || 0
        }))
    } catch {
        recentReports.value = [
            { type: "Flood", area: "Birmingham", votes: 23 },
            { type: "Road blocked", area: "Coventry", votes: 15 },
            { type: "Power Outage", area: "Wolverhampton", votes: 9 }
        ]
    }
}

onMounted(() => {
    // loadRecentReports()
})

function getIconColor(type) {
    const colors = {
        'Flood': '#2563eb',
        'Wildfire': '#dc2626',
        'Storm Damage': '#7c3aed',
        'Road blocked': '#ea580c',
        'Power Outage': '#ca8a04',
        'Landslide': '#92400e',
        'Infrastructure Damage': '#0f766e'
    }
    return colors[type] || '#4f46e5'
}
const goToReports = () => router.push('/reports')
const goToHabitabilityView = () => router.push('/habitability-score')
</script>

<style scoped>
.home-page {
    min-height: 100vh;
    background: var(--background);
}

.hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 3rem;
    background: var(--container);
    color: var(--on-container);
}

.hero-content h1 {
    font-size: 3rem;
    line-height: 1.1;
    margin: 0;
    margin-bottom: 1rem;
}

.subtitle {
    font-size: 1.25rem;
    max-width: 520px;
    margin: 0;
    margin-bottom: 1rem;
}

.cta-buttons {
    display: flex;
    gap: 1rem;
    margin: 0;
}

.btn-primary, .btn-secondary {
    padding: 1rem 2rem;
    border-radius: 9999px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
}

.btn-primary {
    background: var(--background);
    color: var(--on-background);
}

.btn-secondary {
    background: transparent;
    color: var(--on-container);
    border: 2px solid var(--background);
}

.score-card {
    background: var(--background);
    color: var(--on-background);
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 1rem 2rem rgba(var(--shadow), var(--shadow-alpha));
}

h3 {
    color: var(--on-background);
    font-size: 1.25rem;
    margin: 0;
    margin-bottom: 1rem;
}

h2 {
    margin: 0 auto;
    margin-bottom: 2rem;
}

.score-circle {
    width: 140px;
    height: 140px;
    background: var(--on-background);
    border-radius: 9999px;
    margin: 0 auto;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    font-size: 2.5rem;
    font-weight: 600;
    color: var(--background);
}

.score-detail {
    margin: 0 auto;
    font-size: 1rem;
    color: var(--on-background);
}

.features {
    padding: 3rem;
    background: var(--background);
}

.features h2 {
    text-align: center;
    margin-bottom: 40px;
    color: #1e293b;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
}

.feature-card {
    background: var(--background);
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
}

.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 30px rgba(0,0,0,0.1);
}

.feature-card .icon {
    font-size: 3rem;
    margin-bottom: 16px;
}

.recent-reports {
    padding: 3rem;
    background: var(--surface);
}

.reports-teaser {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.teaser-card {
    background: white;
    padding: 16px 20px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    cursor: pointer;
}

.type {
    padding: 4px 12px;
    border-radius: 9999px;
    color: white;
    font-size: 0.85rem;
    font-weight: 600;
}

.view-all-btn {
    margin-top: 24px;
    background: #3b82f6;
    color: white;
    border: none;
    padding: 12px 28px;
    border-radius: 9999px;
    cursor: pointer;
}
</style>
