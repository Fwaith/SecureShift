<template>
    <div class="map-page">
        <div class="map-container">
            <l-map 
                ref="mapRef"
                v-model:zoom="zoom" 
                :center="center" 
                class="leaflet-map"
            >
                <l-tile-layer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution="&copy; OpenStreetMap contributors"
                />

                <l-marker
                    v-for="report in filteredReports"
                    :key="report.id"
                    :lat-lng="[report.lat, report.lng]"
                    :icon="getIcon(report.type)"
                    @click="openPopup(report)"   
                >
                    <l-popup :options="{ autoPan: true, closeButton: true }">
                        <div class="popup-card">
                            <h3>{{ report.type }}</h3>
                            <p><strong>Location:</strong> {{ report.area }}</p>
                            <p><strong>Severity:</strong> {{ report.severity }}</p>
                            <p><strong>Status:</strong> {{ report.status }}</p>
                            <p><strong>Votes:</strong> {{ report.votes }}</p>
                        </div>
                    </l-popup>
                </l-marker>
            </l-map>
        </div>

        <div class="reports-section">
            <div class="reports-header">
                <h2>Community Reports</h2>
                
                <div class="controls">
                    <input
                        v-model="searchTerm"
                        type="text"
                        placeholder="Search by area or type..."
                        class="search-input"
                    />
                    
                    <select v-model="filterType" class="filter-select">
                        <option value="">All Types</option>
                        <option v-for="type in disasterTypes" :key="type" :value="type">
                            {{ type }}
                        </option>
                    </select>

                    <select v-model="sortBy" class="filter-select">
                        <option value="votes">Most Voted</option>
                        <option value="recent">Most Recent</option>
                    </select>
                </div>
            </div>

            <div class="reports-grid">
                <div 
                    v-for="report in filteredReports" 
                    :key="report.id"
                    class="report-card"
                    @click="openPopup(report)"
                >
                    <div class="card-header">
                        <span class="type-badge" :style="{ backgroundColor: getIconColor(report.type) }">
                            {{ report.type }}
                        </span>
                        <span class="status-badge" :class="report.status.toLowerCase().replace(' ', '-')">
                            {{ report.status }}
                        </span>
                    </div>

                    <h4>{{ report.area }}</h4>
                    <p class="severity">Severity: <strong>{{ report.severity }}</strong></p>
                    
                    <div class="vote-section">
                        <button 
                            class="vote-btn"
                            @click.stop="upvote(report)"
                        >
                            ▲ Upvote
                        </button>
                        <span class="vote-count">{{ report.votes }} votes</span>
                    </div>

                    <small class="timestamp">
                        {{ new Date(report.timestamp).toLocaleDateString() }}
                    </small>
                </div>
            </div>

            <div v-if="resolvedReports.length" class="resolved-teaser">
                <h3>Previously Resolved ({{ resolvedReports.length }})</h3>
                <p>Click to view full archive →</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import * as L from 'leaflet'
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet"
import "leaflet/dist/leaflet.css"

const zoom = ref(9)
const center = ref([52.4862, -1.8904])
const mapRef = ref(null)

const reports = ref([])

const disasterTypes = [
    'Flood', 'Wildfire', 'Storm Damage', 'Road blocked',
    'Power Outage', 'Landslide', 'Infrastructure Damage'
]

const areas = [
    'Birmingham', 'Coventry', 'Wolverhampton', 'Dudley',
    'Walsall', 'Solihull', 'Sandwell', 'West Bromwich'
]

const areaCenters = {
    'Birmingham':    [52.4862, -1.8904],
    'Coventry':      [52.4082, -1.5105],
    'Wolverhampton': [52.5860, -2.1290],
    'Dudley':        [52.5084, -2.0877],
    'Walsall':       [52.5853, -1.9825],
    'Solihull':      [52.4141, -1.7750],
    'Sandwell':      [52.5210, -1.9940],
    'West Bromwich': [52.5210, -1.9940]
}

const severities = ['Low', 'Medium', 'High']
const statuses = ['Pending', 'In Progress', 'Resolved']

const westMidlandsBounds = {
    minLat: 52.2, maxLat: 52.7,
    minLng: -2.4, maxLng: -1.3
}

const searchTerm = ref('')
const filterType = ref('')
const sortBy = ref('votes')  

function randomInRange(min, max) {
    return min + Math.random() * (max - min)
}

function randomItem(array) {
    return array[Math.floor(Math.random() * array.length)]
}

function generateReports() {
    reports.value = []
    for (let i = 0; i < 12; i++) {
        const area = randomItem(areas)              
        const [centerLat, centerLng] = areaCenters[area]
        
        reports.value.push({
            id: i + 1,
            lat: centerLat + randomInRange(-0.035, 0.035),   
            lng: centerLng + randomInRange(-0.035, 0.035),
            type: randomItem(disasterTypes),
            area: area,                                    
            severity: randomItem(severities),
            status: randomItem(statuses),
            votes: Math.floor(Math.random() * 47) + 3,
            timestamp: Date.now() - Math.random() * 1000000000
        })
    }
}

const filteredReports = computed(() => {
    let result = reports.value.filter(report => {
        const matchesSearch = 
            !searchTerm.value ||
            report.area.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
            report.type.toLowerCase().includes(searchTerm.value.toLowerCase())
        
        const matchesType = !filterType.value || report.type === filterType.value
        
        return matchesSearch && matchesType
    })

    if (sortBy.value === 'votes') {
        result.sort((a, b) => b.votes - a.votes)
    } else {
        result.sort((a, b) => b.timestamp - a.timestamp)
    }

    return result
})

const resolvedReports = computed(() => 
    reports.value.filter(r => r.status === 'Resolved')
)

const iconCache = {}
function getIconColor(type) { 
    switch(type) {
        case 'Flood': return '#2563eb'
        case 'Wildfire': return '#dc2626'
        case 'Storm Damage': return '#7c3aed'
        case 'Road blocked': return '#ea580c'
        case 'Power Outage': return '#ca8a04'
        case 'Landslide': return '#92400e'
        case 'Infrastructure Damage': return '#0f766e'
        default: return '#4f46e5'
    }
}

function getIcon(type) {
    if (!iconCache[type]) {
        const color = getIconColor(type)
        iconCache[type] = L.divIcon({
            className: '',
            html: `<div style="width:18px;height:18px;background:${color};border:3px solid white;border-radius:50%;box-shadow:0 2px 8px rgba(0,0,0,0.35);"></div>`,
            iconSize: [18, 18],
            iconAnchor: [9, 9],
            popupAnchor: [0, -10]
        })
    }
    return iconCache[type]
}

function openPopup(report) {
}

function upvote(report) {
    report.votes++
}

onMounted(() => {
    generateReports()
})
</script>

<style scoped>
.map-page {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f8fafc;
}

.map-container {
    height: 60vh;
    position: relative;
}

.leaflet-map {
    width: 100%;
    height: 100%;
}

.reports-section {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: white;
    border-top: 1px solid #e2e8f0;
}

.reports-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
}

.reports-header h2 {
    margin: 0;
    color: #1e293b;
}

.controls {
    display: flex;
    gap: 12px;
}

.search-input, .filter-select {
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 0.95rem;
}

.reports-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
}

.report-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.report-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    border-color: #64748b;
}

.card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
}

.type-badge {
    padding: 4px 12px;
    border-radius: 9999px;
    color: white;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-badge {
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 500;
}
.status-badge.pending { background: #fbbf24; color: #78350f; }
.status-badge.in-progress { background: #60a5fa; color: white; }
.status-badge.resolved { background: #34d399; color: white; }

.vote-section {
    margin-top: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.vote-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 6px 14px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
}

.vote-count {
    font-weight: 600;
    color: #1e40af;
}

.timestamp {
    color: #64748b;
    font-size: 0.85rem;
}

.resolved-teaser {
    margin-top: 30px;
    padding: 16px;
    background: #f1f5f9;
    border-radius: 8px;
    text-align: center;
    color: #475569;
}

.popup-card {
    min-width: 240px;
}
.popup-card h3 { margin: 0 0 10px; color: #1e293b; }
.popup-card p { margin: 6px 0; color: #475569; }
</style>
