import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ReportsView from '../views/ReportsView.vue'
import ForecastView from '../views/ForecastView.vue'
import AuthorityView from '../views/AuthorityView.vue'

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/home', name: 'home', component: HomeView },
    { path: '/reports', name: 'reports', component: ReportsView },
    { path: '/forecast', name: 'forecast', component: ForecastView },
    { path: '/authority', name: 'authority', component: AuthorityView },
    { path: '/reports/:reportId', name: 'ReportDetail', component: () => import('../views/ReportDetail.vue')},
    { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
