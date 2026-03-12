<template>
    <div class="login-container">
        <div class="login-card">

            <div class="login-header">
                <h1>SecureShift</h1>
                <p>Sign in to your account</p>
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
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
    email: '',
    password: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')

const API = `${import.meta.env.VITE_API_URL}/api/v1`

const handleLogin = async () => {
    error.value = ''
    success.value = ''
    loading.value = true

    try {
        const res = await fetch(`${API}/auth/login`, {
            method: 'POST',
            headers: {
             'Content-Type': 'application/json'
            },
            body: JSON.stringify(form.value),
            credentials: 'include'
        })

        if (!res.ok) {
            throw new Error('Invalid email or password')
        }

        const userRes = await fetch(`${API}/users/me`, {
            credentials: 'include'
        })

        if (!userRes.ok) {
            throw new Error('Could not load user details')
        }

        await userRes.json()

        success.value = 'Login successful! Redirecting...'
        setTimeout(() => router.push('/'), 800)
  } catch (err) {
    error.value = err.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>

.login-container {
    height: 100vh;
    width: 100vw;

    display: flex;
    justify-content: center;
    align-items: center;

    background: linear-gradient(135deg,#f3f4f6,#e0e7ff);
}

.login-card {
    width: 420px;
    padding: 40px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.12);
}

.login-header {
    text-align: center;
    margin-bottom: 30px;
}

.login-header h1 {
    font-size: 40px;
    color: #4f46e5;
}

.login-header p {
    color: #6b7280;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

input {
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #d1d5db;
}

button {
    margin-top: 10px;
    padding: 14px;
    border: none;
    border-radius: 10px;
    background: #4f46e5;
    color: white;
    font-weight: 600;
    cursor: pointer;
}

button:hover {
    background: #4338ca;
}

.login-footer {
    text-align: center;
    margin-top: 20px;
}

.error {
    color: red;
    text-align: center;
    margin-top: 10px;
}

.success {
    color: green;
    text-align: center;
    margin-top: 10px;
}

</style>
