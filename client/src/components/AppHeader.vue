<template>
    <header class="header">
        <div class="logo">
            <router-link to="/home" class="logo-link">
                <img src="/logo.svg" alt="Logo" class="logo-image"/>
                <span class="logo-text">SecureShift</span>
            </router-link>
        </div>

        <nav class="nav">
            <router-link to="/home" class="nav-link">Home</router-link>
            <router-link to="/habitability-score" class="nav-link">Habitability</router-link>
            <router-link to="/forecast" class="nav-link">Forecast</router-link>
            <router-link to="/reports" class="nav-link">Reports</router-link>
            <router-link v-if="showAuthorityLink" to="/authority" class="nav-link">Authority</router-link>
        </nav>

        <div class="button-group">
            <button @click="$router.push('/login')" class="login-button">
                Login
            </button>
            <span class="divider"></span>
            <button @click="openAccessibility" class="accessibility-button">
                <img src="/accessibility-logo-light.svg" alt="Accessibility Logo" class="accessibility-logo"/>
            </button>
        </div>
    </header>
</template>

<script setup>
import { onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { useAccessibility } from "../composables/useAccessibility"
import api from "../services/api"

const { openAccessibility } = useAccessibility()
const route = useRoute()
const showAuthorityLink = ref(false)

async function refreshAuthorityVisibility() {
    try {
        const response = await api.get("/users/me")
        showAuthorityLink.value = response?.data?.is_admin === true
    } catch {
        showAuthorityLink.value = false
    }
}

onMounted(() => {
    refreshAuthorityVisibility()
})

watch(
    () => route.fullPath,
    () => {
        refreshAuthorityVisibility()
    }
)
</script>

<style scoped>
.header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 3rem;
    background: var(--background);
    border-bottom: 1px solid var(--on-background);
    position: static;
    top: 0;
    z-index: auto;
}

.logo {
    display: flex;
    justify-content: left;
    flex: 1;
}

.logo-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.logo-image {
    width: auto;
    height: 2rem;
}

.logo-text {
    font-size: 1.75rem;
    font-weight: 300;
    color: var(--on-background);
    text-decoration: none;
}

.nav {
    display: flex;
    margin: 0 auto;
    gap: 1.5rem;
    justify-content: center;
    margin: 0 1rem;
}

.nav-link {
    text-decoration: none;
    font-size: 0.9rem;
    color: var(--on-background);
    font-weight: 500;
}

.nav-link:hover {
    filter: brightness(2.5);
}

.button-group {
    display: flex;
    flex: 1;
    gap: 1rem;
    justify-content: right;
    align-items: center;
}

.login-button {
    cursor: pointer;
    background: var(--primary);
    color: var(--on-primary);
    padding: 0;
    border: none;
    border-radius: 10px;
    width: 5rem;
    height: 2rem;
}

.login-button:hover {
    filter: brightness(0.85);
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(var(--shadow), var(--shadow-alpha));
}

.divider {
    width: 1px;
    height: 2rem;
    background-color: var(--on-background);
    display: inline-block;
}

.accessibility-button {
    display: flex;
    padding: 0;
    border: none;
    background-color: rgba(0, 0, 0, 0);
    margin: 0;
    cursor: pointer;
}

.accessibility-logo {
    width: 2.5rem;
    height: auto;
}

.accessibility-button:hover {
    filter: brightness(0.85);
    transform: translateY(-2px);
}
</style>
