<template>
    <header class="header">
        <router-link to="/home" class="logo-text">
            SecureShift
        </router-link>

        <nav class="nav">
            <router-link to="/home" class="nav-link">Home</router-link>
            <router-link to="/reports" class="nav-link">Reports</router-link>
            <router-link to="/forecast" class="nav-link">Forecast</router-link>
            <router-link to="/authority" class="nav-link">Authority</router-link>
        </nav>

        <button @click="openAccessibility" class="accessibility-button">
            Accessibility
        </button>
    </header>
</template>

<script setup>
import { useAccessibility } from "../composables/useAccessibility"

const { openAccessibility } = useAccessibility()
</script>

<style scoped>
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

.logo-text {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1e293b;
    text-decoration: none;
}

.nav {
    display: flex;
    gap: 24px;
}

.nav-link {
    text-decoration: none;
    color: #475569;
    font-weight: 500;
}

.accessibility-button {
    background: #64748b;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 9999px;
    cursor: pointer;
    font-weight: 600;
}
</style>
