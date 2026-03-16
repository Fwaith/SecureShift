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
                    Real-time habitability scores • Community reporting • 
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
                <p class="score-detail">Moderate • Stable • 3 active reports</p>
            </div>
        </section>
        <footer class="footer">
            <p>SecureShift Prototype • WCAG 2.0 Level A • Data from ONS, UK AIR, Police.uk & OpenStreetMap</p>
            <p class="accessibility-note">Accessibility settings are saved globally for all users.</p>
        </footer>
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

.footer {
    text-align: center;
    padding: 40px;
    background: #1e293b;
    color: #94a3b8;
    font-size: 0.9rem;
}

.accessibility-note {
    margin-top: 8px;
    font-size: 0.85rem;
    opacity: 0.8;
}
</style>
