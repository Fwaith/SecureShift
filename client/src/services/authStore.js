import { reactive } from 'vue'
import api from './api'

export const authStore = reactive({
    isLoggedIn: false,
    isAdmin: false,
    user: null,
    isInitialized: false,

    async checkAuth() {
        if (this.isInitialized) return

        try {
            const response = await api.get("/users/me")
            this.isLoggedIn = true
            this.isAdmin = response?.data?.is_admin === true
            this.user = response?.data
        } catch {
            this.isLoggedIn = false
            this.isAdmin = false
        } finally {
            this.isInitialized = true
        }
    },

    async logout() {
        try {
            await api.post("/auth/logout")
        } finally {
            this.isLoggedIn = false
            this.isAdmin = false
            this.user = null
            window.location.href = '/home'
        }
    }
})
