<template>
    <div class="register-container">
        <div class="register-card">
            <div class="register-header">
                <h1>SecureShift</h1>
                <p v-if="!showOTPForm">Create your account</p>
                <p v-else>Verify your email</p>
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
                <p>
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
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

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

const handleRegister = async () => {
    error.value = ''
    success.value = ''

    const registerData = {
        username: form.value.username,
        email: form.value.email,
        phoneNumber: `${form.value.phoneCode}${form.value.phoneNumber}`,
        postcode: form.value.postcode,
        password: form.value.password
    }

    try {
        const res = await fetch(`${API}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(registerData),
            credentials: 'include'
        })

        const data = await res.json().catch(() => ({}))
        if (!res.ok) throw new Error(data.message || 'Registration failed')
        
        success.value = 'Registration successful. OTP sent to your email.'
        showOTPForm.value = true
    } catch (err) {
        error.value = err.message
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
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #f3f4f6, #e0e7ff);
}

.register-card {
  width: 100%;
  max-width: 980px;
  max-height: 90vh;
  overflow-y: auto;
  background: #ffffff;
  border-radius: 24px;
  padding: 36px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.1);
}

.register-header {
    text-align: center;
    margin-bottom: 28px;
}

.register-header h1 {
    margin: 0;
    font-size: 2.75rem;
    color: #4f46e5;
    line-height: 1.1;
}

.register-header p {
    margin-top: 10px;
    color: #6b7280;
    font-size: 1rem;
}

.register-form {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.section-title {
    margin-top: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #4f46e5;
    padding-bottom: 6px;
    border-bottom: 1px solid #e5e7eb;
}

.form-row {
    display: flex;
    gap: 16px;
}

.form-group {
    display: flex;
    flex-direction: column;
    flex: 1;
}

.form-group label {
    margin-bottom: 6px;
    font-weight: 600;
    color: #334155;
}

.phone-row {
    display: flex;
    gap: 10px;
}

.phone-row select {
    width: 110px;
}

.phone-row input {
    flex: 1;
}

input,
select {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    font-size: 0.98rem;
    box-sizing: border-box;
    background: #ffffff;
}

input:focus,
select:focus {
    outline: none;
    border-color: #4f46e5;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

.checkbox-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.checkbox-group input {
    width: auto;
}

.checkbox-group label {
    color: #475569;
}

button {
    margin-top: 4px;
    padding: 14px;
    border: none;
    border-radius: 12px;
    background: #4f46e5;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s ease, opacity 0.2s ease;
}

button:hover {
    background: #4338ca;
}

button:disabled {
    opacity: 0.65;
    cursor: not-allowed;
}

.secondary-button {
    background: #e5e7eb;
    color: #1f2937;
}

.secondary-button:hover {
    background: #d1d5db;
}

.otp-form {
    max-width: 420px;
    margin: 0 auto;
}

.otp-message {
    text-align: center;
    color: #475569;
}

.register-footer {
    text-align: center;
    margin-top: 20px;
}

.register-footer a {
    color: #4f46e5;
    text-decoration: none;
    font-weight: 500;
}

.register-footer a:hover {
    text-decoration: underline;
}

.message {
    text-align: center;
    margin-top: 14px;
    font-weight: 500;
}

.error {
    color: #dc2626;
}

.success {
    color: #16a34a;
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
