<template>
    <AppLayout>
        <div class="register-container">
            <div class="register-card" :class="{ 'otp': showOTPForm }">
                <div class="register-header">
                    <h1 v-if="!showOTPForm">Create your account</h1>
                    <h1 v-else>Verify your email</h1>
                </div>

                <form v-if="!showOTPForm" @submit.prevent="handleRegister" class="register-form">
                    <div class="form-group">
                        <label>Username</label>
                        <input v-model="form.username" type="text" required />
                    </div>

                    <div class="form-group">
                        <label>Email</label>
                        <input v-model="form.email" type="email" required />
                    </div>

                    <div class="form-group">
                        <label>Phone Number</label>
                        <div class="phone-row">
                            <select v-model="form.phoneCode" required>
                                <option v-for="code in countryCodes" :key="code" :value="code">{{ code }}</option>
                            </select>
                            <input
                                v-model.trim="form.phoneNumber"
                                type="tel"
                                placeholder="Your phone number"
                                required
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Postcode</label>
                        <input v-model="form.postcode" type="text" required />
                    </div>

                    <div class="form-group">
                        <label for="password">Password</label>
                        <input
                            id="password"
                            v-model="form.password"
                            :type="showPassword ? 'text' : 'password'"
                            placeholder="Minimum 8 characters"
                            minlength="8"
                            required
                        />
                    </div>

                    <div class="checkbox-group">
                        <input id="showPassword" v-model="showPassword" type="checkbox" />
                        <label for="showPassword">Show Password</label>
                    </div>

                    <button type="submit" :disabled="loading">
                        {{ loading ? 'Registering...' : 'Register' }}
                    </button>
                </form>

                <form v-else @submit.prevent="handleVerifyOTP" class="register-form otp-form">
                    <div class="otp-message">
                        <p class="otp-text">
                            We sent a verification code to
                            <strong>{{ form.email }}</strong>
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="otp">OTP</label>
                        <input
                            id="otp"
                            v-model.trim="otp"
                            type="text"
                            placeholder="Enter 6-digit OTP"
                            maxlength="6"
                            required
                        />
                    </div>

                    <button type="submit" :disabled="loading">
                        {{ loading ? 'Verifying...' : 'Verify OTP' }}
                    </button>

                    <button type="button" class="secondary-button" @click="goBackToRegister" :disabled="loading">
                        Back
                    </button>
                </form>

                <div class="register-footer">
                    <router-link to="/login">Already have an account? Sign In</router-link>
                </div>

                <p v-if="error" class="message error">{{ error }}</p>
                <p v-if="success" class="message success">{{ success }}</p>
            </div>
        </div>
    </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from "../components/AppLayout.vue"

const router = useRouter()

const form = ref({
    username: '',
    email: '',
    phoneCode: '+44',
    phoneNumber: '',
    postcode: '',
    password: ''
})

const otp = ref('')
const showOTPForm = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref('')
const showPassword = ref(false)

const countryCodes = ['+44', '+60', '+65', '+1', '+61', '+91', '+86']

const API = `${import.meta.env.VITE_API_URL}/api/v1` 
console.log('API:', API)

const handleRegister = async () => {
    error.value = ''
    success.value = ''
    loading.value = true
    console.log("REGISTER CLICKED")

    const registerData = {
        username: form.value.username,
        email: form.value.email,
        phoneNumber: `${form.value.phoneCode}${form.value.phoneNumber}`,
        postcode: form.value.postcode,
        password: form.value.password
    }

    try {
        console.log('sending registration data: ', registerData)
        const res = await fetch(`${API}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(registerData),
            credentials: 'include'
        })

        const data = await res.json().catch(() => ({}))
        console.log('Response from backend: ', data)
        if (!res.ok) throw new Error(data.message || 'Registration failed')
        
        success.value = 'Registration successful. OTP sent to your email.'
        showOTPForm.value = true
    } catch (err) {
        console.error('Registration error: ', err)
        error.value = err.message || 'Registration failed. Please check if backend is running.'
    } finally {
        loading.value = false
    }
}

const handleVerifyOTP = async () => {
    error.value = ''
    success.value = ''
    loading.value = true

    try {
        const res = await fetch(`${API}/auth/verify-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: form.value.email,
                otp: otp.value
            }),
            credentials: 'include'
        })

        let data = {}
        try {
            data = await res.json()
        } catch {
            data = {}
        }

        if (!res.ok) {
            throw new Error(data.message || 'Invalid OTP.')
        }

        success.value = 'Account verified. Redirecting to login...'
        setTimeout(() => router.push('/login'), 1200)
    } catch (err) {
        error.value = err.message || 'Verification failed. Please try again.'
    } finally {
        loading.value = false
    }
}

const goBackToRegister = () => {
    showOTPForm.value = false
    otp.value = ''
    error.value = ''
    success.value = ''
}
</script>

<style scoped>
.register-container {
    width: auto;
    height: auto;
    display: flex;
    justify-content: center;
    align-items: center;
    background: var(--surface);
}

.register-card {
    padding: 3rem;
    margin: 3rem;
    width: 50rem;
    height: auto;
    background: var(--background);
    border-radius: 10px;
    box-shadow: 0 1rem 2rem rgba(var(--shadow), var(--shadow-alpha));
}

.register-card.otp{
    width: 25rem;
}

.register-header {
    text-align: left;
}

.register-header h1 {
    margin: 0;
    padding: 0;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
    color: var(--on-background);
}

.register-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    flex: 1;
}

.form-group label {
    margin-bottom: 0.5rem;
    font-size: 1rem;
    color: var(--on-background);
}

.phone-row {
    display: flex;
    gap: 1rem;
}

.phone-row select {
    flex: 1;
}

.phone-row input {
    flex: 9;
}

input,
select {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid var(--outline);
    border-radius: 10px;
    background: var(--background);
    color: var(--on-background);
}

input:focus,
select:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--primary);
}

.checkbox-group {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.checkbox-group input {
    width: auto;
}

.checkbox-group label {
    color: var(--on-background);
}

button {
    margin-top: 1rem;
    margin-bottom: 1rem;
    padding: 0.8rem;
    border: none;
    border-radius: 12px;
    background: var(--container);
    color: var(--on-container);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s ease, opacity 0.2s ease;
}

button:hover {
    filter: brightness(0.85);
}

.dark button:hover {
    filter: brightness(1.25);
}

button:disabled {
    opacity: 0.65;
    cursor: not-allowed;
}

.secondary-button {
    margin-top: 0;
    background: var(--surface);
    color: var(--on-surface);
}

.secondary-button:hover {
    filter: brightness(0.85);
}

.dark .secondary-button:hover {
    filter: brightness(1.25);
}

.otp-form {
    margin: 0 auto;
    gap: 1rem;
}

.otp-message {
    text-align: left;
    color: var(--on-background);
}

.otp-text {
    margin: 0;
}

.register-footer {
    text-align: center;
}

.register-footer a {
    color: var(--on-container);
}

.register-footer a:hover {
    filter: brightness(2.5);
}

.dark .register-footer a:hover {
    filter: brightness(0.4);
}

.message {
    text-align: center;
    margin-top: 1rem;
    font-weight: 600;
}

.error {
    color: var(--error);
    text-align: center;
    margin: 0;
    margin-top: 1rem;
}

.success {
    color: var(--success);
    text-align: center;
    margin: 0;
    margin-top: 1rem;
}

@media (max-width: 768px) {
    .register-card {
        padding: 24px;
    }

    .form-row {
        flex-direction: column;
        gap: 18px;
    }

    .phone-row {
        flex-direction: column;
    }

    .phone-row select {
        width: 100%;
    }

    .register-header h1 {
        font-size: 2.2rem;
    }
}
</style>
