<template>
    <footer class="footer">
        <div class="content">
            <div class="about">
                <div class="logo">
                    <img src="/logo.svg" alt="Logo" class="logo-image"/>
                    <span class="logo-text">SecureShift</span>
                </div>
                <p class="tagline">SecureShift provides habitability score and issue reporting to help residents and authorities make informed decisions.</p>
                <button @click="scrolltoTop">
                    <span class="button-text">BACK TO TOP</span>
                    <img />
                </button>
            </div>
            <div class="features">
                <span class="category">Features</span>
                <nav>
                    <router-link to="/habitability" class="nav-link">Habitability</router-link>
                    <router-link to="/forecast" class="nav-link">Forecast</router-link>
                    <router-link to="/reports" class="nav-link">Reports</router-link>
                    <router-link v-if="showAuthorityLink" to="/authority" class="nav-link">Authority</router-link>
                </nav>
            </div>
            <div class="account">
                <span class="category">Account</span>
                <nav>
                    <template v-if="!isLoggedIn">
                        <router-link to="/login" class="nav-link">Login</router-link>
                        <router-link to="/register" class="nav-link">Register</router-link>
                    </template>
                    <template v-else>
                        <a href="#" @click.prevent="authStore.logout()" class="nav-link">Logout</a>
                    </template>
                </nav>
            </div>
        </div>
        <div class="footnote">
            <span class="footnote-text">SecureShift Prototype – SDG 11 Project</span>
        </div>
    </footer>
</template>

<script setup>
import { onMounted, watch, computed } from "vue"
import { useRoute } from "vue-router"
import { authStore } from "../services/authStore"

const route = useRoute()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const showAuthorityLink = computed(() => authStore.isAdmin)

const scrolltoTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
    authStore.checkAuth()
})

watch(() => route.fullPath, () => {
    authStore.checkAuth()
})
</script>

<style scoped>
.footer {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.content {
    display: flex;
    flex-wrap: wrap;
    background: var(--on-container);
    padding: 2rem 8rem;
    gap: 2rem;
    width: 100%;
    color: var(--on-primary);
}

.about {
    display: flex;
    flex: 4;
    flex-direction: column;
    gap: 1.5rem;
}

.logo {
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
    text-decoration: none;
}

.tagline {
    padding: 0;
    margin: 0;
    width: 30rem;
}

button {
    display: flex;
    width: fit-content;
    height: 2rem;
    border: 1px solid var(--on-primary);
    border-radius: 10px;
    color: var(--on-primary);
    background: var(--on-container);
}

.button-text {
    margin: 0.5rem;
    font-size: 0.8rem;
}

.features, .account{
    display: flex;
    flex: 1;
    flex-direction: column;
    padding: 1rem;
    padding-top: 0;
    align-items: flex-start;
    font-size: 1rem;
}

nav {
    display: flex;
    flex-direction: column;
}

.nav-link {
    color: var(--background);
    filter: brightness(0.75);
}

.dark .nav-link:hover {
    filter: brightness(1.9);
}

.category {
    padding-bottom: 1rem;
}

.footnote {
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--container);
    width: 100%;
    font-size: 0.8rem;
}

.footnote-text {
    margin: 0.4rem;
}
</style>
