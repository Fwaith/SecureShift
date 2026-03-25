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
    background: #f8fafc;
    font-family: system-ui, sans-serif;
}

.hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 80px 40px;
    background: linear-gradient(135deg, #1e40af, #3b82f6);
    color: white;
    gap: 40px;
}

.hero-content h1 {
    font-size: 3.2rem;
    line-height: 1.1;
    margin: 0;
}

.subtitle {
    font-size: 1.25rem;
    max-width: 520px;
    opacity: 0.95;
}

.cta-buttons {
    display: flex;
    gap: 16px;
    margin-top: 30px;
}

.btn-primary, .btn-secondary {
    padding: 16px 32px;
    border-radius: 9999px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
}

.btn-primary {
    background: white;
    color: #1e40af;
}

.btn-secondary {
    background: transparent;
    color: white;
    border: 2px solid white;
}

.score-card {
    background: white;
    color: #1e293b;
    padding: 30px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    min-width: 260px;
}

.score-circle {
    width: 140px;
    height: 140px;
    background: #f1f5f9;
    border-radius: 9999px;
    margin: 20px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    font-size: 2.8rem;
    font-weight: 700;
    color: #1e40af;
}

.score-detail {
    font-size: 1rem;
    color: #64748b;
}

.features {
    padding: 60px 40px;
    background: white;
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
    background: #f8fafc;
    padding: 32px;
    border-radius: 16px;
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
    padding: 60px 40px;
    background: #f8fafc;
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
