<template>
    <div class="home-page">
        <header class="header">
            <div class="logo">
                <span class="logo-text">SecureShift</span>
            </div>

            <nav class="nav">
                <router-link to="/habitability" class="nav-link">Habitability Overview</router-link>
                <router-link to="/reports" class="nav-link">Report an Issue</router-link>
                <router-link to="/historical" class="nav-link">Historical Data</router-link>
                <router-link to="/forecast" class="nav-link">Forecast</router-link>
            </nav>

            <button @click="toggleAccessibilityMenu" class="accessibility-button">
                Accessibility
            </button>
        </header>

        <section class="hero">
            <div class="hero-content">
                <h1>Know Your Area. <br>Protect you community.</h1>
                <p class="subtitle">
                    Real-time habitability scores ~ Community reporting ~ 
                    Built for everyone (WCAG Level A compliant)
                </p>
                <div class="cta-buttons">
                    <button @click="goToHabitability" class="btn-primary">
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
                <div class="feature-card" @click="goToHabitability">
                    <h3>Habitability Overview</h3>
                    <p>Interactive map with choropleth layers, comparison tool, and detailed metrics using the official formula.</p>
                </div>

                <div class="feature-card" @click="goToReports">
                    <h3>Report Issues</h3>
                    <p>Map markers + searchable cards. Vote, track status (Pending/In Progress/Resolved).</p>
                </div>

                <div class="feature-card" @click="toggleAccessibilityMenu">
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

        <footer class="footer">
            <p>SecureShift Prototype ~ WCAG 2.0 Level A ~ Data from ONS, UK AIR, Police.uk & OpenStreetMap</p>
        </footer>

        <div v-if="showAccessibilityMenu" class="accessibility-modal" @click.self="toggleAccessibilityMenu">
            <div class="modal-content">
                <h3>Accessibility Settings</h3>
                
                <div class="setting">
                    <label>Text Size</label>
                    <input type="range" v-model="textSize" min="80" max="150" @input="applyAccessibility" />
                    <span>{{ textSize }}%</span>
                </div>

                <div class="setting">
                    <label>Dyslexic Font</label>
                    <button @click="toggleDyslexicFont" class="toggle-btn">
                        {{ useDyslexicFont ? 'ON' : 'OFF' }} (OpenDyslexic)
                    </button>
                </div>

                <div class="setting">
                    <label>Colour-blind Mode</label>
                    <select v-model="colorMode" @change="applyAccessibility">
                        <option value="normal">Normal</option>
                        <option value="deuteranopia">Deuteranopia (Green-Blind)</option>
                        <option value="protanopia">Protanopia (Red-Blind)</option>
                        <option value="tritanopia">Tritanopia (Blue-Blind)</option>
                    </select>
                </div>

                <button @click="toggleAccessibilityMenu" class="close-btn">Close & Save</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const recentReports = ref([
    { type: "Flood", area: "Birmingham", votes: 23 },
    { type: "Road blocked", area: "Coventry", votes: 15 },
    { type: "Power Outage", area: "Wolverhampton", votes: 9 }
])

const showAccessibilityMenu = ref(false)
const textSize = ref(100)
const useDyslexicFont = ref(false)
const colorMode = ref("normal")

function toggleAccessibilityMenu() {
    showAccessibilityMenu.value = !showAccessibilityMenu.value
}
function toggleDyslexicFont() {
    useDyslexicFont.value = !useDyslexicFont.value
    applyAccessibility()
}

function applyAccessibility() {
    document.documentElement.style.fontSize = `${textSize.value}%`
    if (useDyslexicFont.value) {
        document.documentElement.style.fontFamily = "'OpenDyslexic', sans-serif"
    } else {
        document.documentElement.style.fontFamily = "system-ui, sans-serif"
    }
}

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

const goToHabitability = () => alert("→ Habitability Overview (Feature 3) would open here")
const goToReports = () => alert("→ Resident Reporting Centre (Feature 6) would open here – your MapView.vue")
</script>

<style scoped>
.home-page {
    min-height: 100vh;
    background: #f8fafc;
    font-family: system-ui, sans-serif;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 40px;
    background: white;
    border-bottom: 1px solid #e2e8f0;
    position: sticky;
    top: 0;
    z-index: 10;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.8rem;
    font-weight: 700;
    color: #1e293b;
}

.logo-icon { font-size: 2rem; }

.nav {
    display: flex;
    gap: 24px;
}

.nav-link {
    text-decoration: none;
    color: #475569;
    font-weight: 500;
    transition: color 0.2s;
}

.nav-link:hover { color: #3b82f6; }

.accessibility-btn {
    background: #64748b;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 9999px;
    cursor: pointer;
    font-weight: 600;
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

.footer {
    text-align: center;
    padding: 40px;
    background: #1e293b;
    color: #94a3b8;
    font-size: 0.9rem;
}

.accessibility-modal {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.modal-content {
    background: white;
    padding: 32px;
    border-radius: 16px;
    max-width: 420px;
    width: 100%;
}

.setting {
    margin-bottom: 24px;
}

.setting label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
}

.toggle-btn, select {
    padding: 10px 16px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: white;
    cursor: pointer;
}

.close-btn {
    width: 100%;
    padding: 14px;
    background: #1e40af;
    color: white;
    border: none;
    border-radius: 8px;
    margin-top: 16px;
}
</style>
