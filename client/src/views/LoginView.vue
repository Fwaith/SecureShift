<template>
    <AppLayout>
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <h1>Sign in to your account</h1>
                </div>
                <form @submit.prevent="handleLogin" class="login-form">
                    <div class="form-group">
                        <label>Email</label>
                        <input
                            v-model="form.email"
                            type="email"
                            placeholder="you@example.com"
                            required
                        />
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input
                            v-model="form.password"
                            type="password"
                            required
                        />
                    </div>
                    <button type="submit" :disabled="loading">
                        {{ loading ? "Signing in..." : "Sign In" }}
                    </button>
                </form>
                <div class="login-footer">
                    <router-link to="/register">Don't have an account? Register</router-link>
                </div>
                <p v-if="error" class="error">{{ error }}</p>
                <p v-if="success" class="success">{{ success }}</p>
            </div>
        </div>
    </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from "../components/AppLayout.vue"
import { authStore } from "../services/authStore"

const router = useRouter()

const form = ref({
    email: '',
    password: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')

const API = `${import.meta.env.VITE_API_URL}/api/v1`
console.log('API: ', API)

const handleLogin = async () => {
    error.value = ''
    success.value = ''
    loading.value = true

    try {
        const res = await fetch(`${API}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(form.value),
            credentials: 'include' 
        })
        
        const data = await res.json().catch(() => ({}))

        if (!res.ok) {
            throw new Error(data.message || 'Invalid email or password')
        }

        authStore.isInitialized = false;
        success.value = 'Login successful! Redirecting...'

        setTimeout(() => {
            router.push('/home')
        }, 800)

    } catch (err) {
        error.value = err.message || 'Login failed. Please try again.'
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>

.login-container {
    height: auto;
    width: auto;

    display: flex;
    justify-content: center;
    align-items: center;

    background: var(--surface);
}

.login-card {
    width: 25rem;
    height: auto;
    padding: 3rem;
    margin: 3rem;
    background: var(--background);
    border-radius: 10px;
    box-shadow: 0 1rem 2rem rgba(var(--shadow), var(--shadow-alpha));
}

.login-header {
    text-align: left;
}

.login-header h1 {
    padding: 0;
    margin: 0;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
    color: var(--on-background);
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
}

input {
    background: var(--background);
    padding: 0.8rem;
    border-radius: 10px;
    border: 1px solid var(--outline);
    color: var(--on-background);
}

input::placeholder {
    color: var(--outline);
}

input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--primary);
}

button {
    margin-top: 1rem;
    margin-bottom: 1rem;
    padding: 0.8rem;
    border: none;
    border-radius: 10px;
    background: var(--container);
    color: var(--on-container);
    font-weight: 600;
    cursor: pointer;
}

button:hover {
    filter: brightness(0.85);
}

.dark button:hover {
    filter: brightness(1.25);
}

.login-footer {
    text-align: center;
}

a {
    color: var(--on-container);
}

a:hover {
    filter: brightness(2.5);
}

.dark a:hover {
    filter: brightness(0.4);
}

label {
    color: var(--on-background);
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.error {
    color: var(--error);
    text-align: center;
    margin: 0;
    margin-top: 1rem;
    font-weight: 600;
}

.success {
    color: var(--success);
    text-align: center;
    margin: 0;
    margin-top: 1rem;
    font-weight: 600;
}

</style>
