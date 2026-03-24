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
            <router-link v-if="authStore.isAdmin" to="/authority" class="nav-link">Authority</router-link>
        </nav>

        <div class="button-group">
            <button v-if="isLoggedIn" @click="authStore.logout()" class="logout-button">
                Logout
            </button>
            <button v-else @click="$router.push('/login')" class="login-button">
                Login
            </button>
            <span class="divider"></span>
            <button @click="openAccessibility" class="accessibility-button">
                <img :src="accessibilityLogoPath" alt="Accessibility Logo" class="accessibility-logo"/>
            </button>
        </div>
    </header>
</template>

<script setup>
import { onMounted, watch, computed } from "vue"
import { useRoute } from "vue-router"
import { useAccessibility } from "../composables/useAccessibility"
import { authStore } from "../services/authStore"

const { openAccessibility, accessibility } = useAccessibility()
const route = useRoute()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const showAuthorityLink = computed(() => authStore.isAdmin)

const accessibilityLogoPath = computed(() => {
    return accessibility.darkMode ? "/accessibility-logo-dark.svg" : "/accessibility-logo-light.svg"
})

onMounted(() => {
    authStore.checkAuth()
})

watch(
    () => route.fullPath,
    () => {
        authStore.checkAuth()
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

.dark .nav-link:hover {
    filter: brightness(0.4);
}

.button-group {
    display: flex;
    flex: 1;
    gap: 1rem;
    justify-content: right;
    align-items: center;
}

.login-button, .logout-button{
    cursor: pointer;
    background: var(--primary);
    color: var(--on-primary);
    padding: 0;
    border: none;
    border-radius: 10px;
    width: auto;
    min-width: 5rem;
    height: auto;
    min-height: 2rem;
}

.login-button:hover, .logout-button:hover {
    filter: brightness(0.75);
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(var(--shadow), var(--shadow-alpha));
}

.dark .login-button:hover, .dark .logout-button:hover {
    filter: brightness(1.25);
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

.dark .accessibility-button:hover {
    filter: brightness(1.25);
    transform: translateY(-2px);
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
