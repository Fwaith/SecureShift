import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ReportsView from '../views/ReportsView.vue'
import MapView from '../views/MapView.vue'
import ForecastView from '../views/ForecastView.vue'
import AuthorityView from '../views/AuthorityView.vue'
import AccessibilityView from '../views/AccessibilityView.vue'

const routes = [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/reports', name: 'reports', component: ReportsView },
    { path: '/map', name: 'map', component: MapView },
    { path: '/forecast', name: 'forecast', component: ForecastView },
    { path: '/authority', name: 'authority', component: AuthorityView },
    { path: '/accessibility', name: 'accessibility', component: AccessibilityView },
    { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
