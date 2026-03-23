import { createRouter, createWebHistory } from 'vue-router'
import api from '../services/api'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ReportsView from '../views/ReportsView.vue'
import ForecastView from '../views/ForecastView.vue'
import AuthorityView from '../views/AuthorityView.vue'
import HabitabilityScoreView from '../views/HabitabilityScoreView.vue'

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/home', name: 'home', component: HomeView },
    { path: '/reports', name: 'reports', component: ReportsView },
    { path: '/forecast', name: 'forecast', component: ForecastView },
    { path: '/habitability-score', name: 'habitability-score', component: HabitabilityScoreView },
    {
        path: '/authority',
        name: 'authority',
        component: AuthorityView,
        meta: { requiresAdmin: true },
    },
    { path: '/reports/:reportId', name: 'ReportDetail', component: () => import('../views/ReportDetail.vue')},
    { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach(async (to) => {
    if (!to.meta.requiresAdmin) {
        return true
    }

    try {
        const response = await api.get('/users/me')
        if (response?.data?.is_admin === true) {
            return true
        }

        return { name: 'home' }
    } catch {
        return { name: 'login' }
    }
})

export default router
