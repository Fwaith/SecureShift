<template>
    <AppLayout>
        <div class="report-page">
            <div class="map-container">
                <l-map 
                    ref="mapRef"
                    v-model:zoom="zoom" 
                    :center="center" 
                    class="leaflet-map"
                >
                    <l-tile-layer
                        :url="isDarkMode ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'"
                        :attribution="isDarkMode ? '&copy; CartoDB' : '&copy; OpenStreetMap contributors'"
                    />
                    <l-marker
                        v-for="report in filteredReportsWithLocation"
                        :key="report.id"
                        :lat-lng="[report.lat, report.lng]"
                        :icon="getIcon(report.type)" 
                    >
                        <l-popup :options="{ autoPan: true, closeButton: true }">
                            <div class="popup-card">
                                <h3>{{ report.type }}</h3>
                                <p><strong>Location:</strong> {{ report.area || 'Not specified' }}</p>
                                <p><strong>Severity:</strong> {{ report.severity || 'N/A' }}</p>
                                <p><strong>Status:</strong> {{ report.status || 'pending' }}</p>
                                <p><strong>Votes:</strong> {{ report.voteCount || report.votes || 0 }}</p>
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

                        <button class="report-issue-btn" @click="showReportModal = true">
                            Report an Issue
                        </button>
                    </div>
                </div>
                
                <div v-if="!reports.length" class="no-reports">
                    <p>No reports found yet. Be the first to report an issue!</p>
                </div>
                <div v-else-if="filteredReports.length === 0" class="no-reports">
                    <p>No matching reports — try changing filters</p>
                </div>

                <div class="reports-grid">
                    <div 
                        v-for="report in filteredReports" 
                        :key="report.id"
                        class="report-card"
                        @click="selectedReport = report"
                    >
                        <div class="card-header">
                            <span class="type-badge" :style="{ backgroundColor: getIconColor(report.type) }">
                                {{ report.type || report.title?.slice(0, 20) || 'Report' }}
                            </span>
                            <span class="status-badge" :class="report.status.toLowerCase().replace(' ', '-')">
                                {{ report.status }}
                            </span>
                        </div>

                        <h4>{{ report.title || report.type || 'Report' }}</h4>
                        <p class="severity">Severity: <strong>{{ report.severity }}</strong></p>
                        <span class="separator"></span>
                        <div class="card-bottom">
                            <div class="vote-section">
                                <button 
                                    type="button"
                                    class="vote-btn"
                                    @mouseenter="isUpHovered = report.id"
                                    @mouseleave="isUpHovered = null"
                                    @click.stop="upvote(report)"
                                >
                                    <img :src="getUpvoteSrc(report)" alt="Upvote" class="upvote-img" />
                                </button>

                                <span class="vote-count">{{ report.voteCount || report.votes || 0 }}</span>

                                <button 
                                    type="button"
                                    class="vote-btn"
                                    @mouseenter="isDownHovered = report.id"
                                    @mouseleave="isDownHovered = null"
                                    @click.stop="removeUpvote(report)"
                                >
                                    <img :src="getDownvoteSrc(report)" alt="Downvote" class="downvote-img" />
                                </button>
                            </div>
                            <small class="timestamp">
                                {{ new Date(report.timestamp).toLocaleDateString() }}
                            </small>
                        </div>
                    </div>
                </div>

                <div v-if="resolvedReports.length" class="resolved-teaser">
                    <h3>Previously Resolved ({{ resolvedReports.length }})</h3>
                    <p>Click to view full archive →</p>
                </div>
            </div>

            <div v-if="showReportModal" class="modal-overlay" @click.self="showReportModal = false">
                <div class="modal-content">
                    <h3>Report a New Issue</h3>
                    <form @submit.prevent="createReport">
                        <div class="form-group">
                            <label for="postcode">Postcode *</label>
                            <input
                                id="postcode"
                                v-model="newReport.postcode"
                                type="text"
                                placeholder="e.g. B76 1AA or B76"
                                required
                                maxlength="8"
                            />
                            <small v-if="newReport.postcode" class="hint">
                                Reports are tied to neighbourhoods. This helps us show your report in the right area.
                            </small>
                        </div>
                        <div class="form-group">
                            <label>Type of Issue *</label>
                            <div class="type-options">
                                <button
                                    v-for="type in disasterTypes"
                                    :key="type"
                                    type="button"
                                    class="type-btn"
                                    :class="{ 'selected': newReport.type === type }"
                                    @click="newReport.type = type"
                                >
                                    {{ type }}
                                </button>
                            </div>
                            <div v-if="newReport.type === 'Other'" class="other-input">
                                <input
                                    v-model="newReport.customType"
                                    type="text"
                                    placeholder="Please specify the issue..."
                                    required
                                />
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Severity *</label>
                            <div class="severity-options">
                                <label class="severity-btn" :class="{ 'selected': newReport.severity === 'Low' }">
                                <input
                                    type="radio"
                                    v-model="newReport.severity"
                                    value="Low"
                                    required
                                />
                                    Low
                                </label>
                                <label class="severity-btn" :class="{ 'selected': newReport.severity === 'Medium' }">
                                <input
                                    type="radio"
                                    v-model="newReport.severity"
                                    value="Medium"
                                />
                                    Medium
                                </label>
                                <label class="severity-btn" :class="{ 'selected': newReport.severity === 'High' }">
                                <input
                                    type="radio"
                                    v-model="newReport.severity"
                                    value="High"
                                />
                                    High
                                </label>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="title">Title / Short Description *</label>
                            <input
                                id="title"
                                v-model="newReport.title"
                                type="text"
                                placeholder="e.g. Flooding near New Street Station"
                                required
                            />
                        </div>

                        <div class="form-group">
                            <label for="description">Additional Details (optional)</label>
                            <textarea
                                id="description"
                                v-model="newReport.description"
                                rows="4"
                                placeholder="More information, exact location, photos if available, etc..."
                            ></textarea>
                        </div>

                        <div class="form-actions">
                            <button type="button" class="cancel-btn" @click="showReportModal = false">
                                Cancel
                            </button>
                            <button type="submit" class="submit-btn" :disabled="isSubmitting || !formIsValid">
                                {{ isSubmitting ? 'Submitting...' : 'Submit Report' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div v-if="selectedReport" class="modal-overlay" @click.self="selectedReport = null">
                <div class="modal-content">
                    <button class="close-modal" @click="selectedReport = null">×</button>

                    <h3>{{ selectedReport.title || selectedReport.type || 'Report' }}</h3>

                    <div class="meta-row">
                        <span class="badge" :style="{ backgroundColor: getIconColor(selectedReport.type) }">
                            {{ selectedReport.type || 'Unknown' }}
                        </span>
                        <span class="badge severity" :class="selectedReport.severity?.toLowerCase()">
                            {{ selectedReport.severity || '—' }}
                        </span>
                        <span class="badge status" :class="selectedReport.status?.toLowerCase() || 'pending'">
                            {{ selectedReport.status || 'Pending' }}
                        </span>
                    </div>

                    <p class="area"><strong>Area:</strong> {{ formatArea(selectedReport.area) || 'Not specified' }}</p>
                    <p><strong>Votes:</strong> {{ selectedReport.voteCount || selectedReport.votes || 0 }}</p>

                    <div class="description-block">
                        <h4>Description</h4>
                    </div>
                    <div class="details">
                        <p class="details-text">{{ selectedReport.description || 'No further details provided.' }}</p>
                    </div>
                    
                    <div class="comments-preview-section">
                        <div class="modal-buttons">
                            <button 
                                class="btn view-full"
                                @click="openFullDiscussion(selectedReport)"
                            >
                                {{ selectedReport.comments?.length ? 'View full discussion →' : 'Start discussion →' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AppLayout>
</template>

<script setup>
import AppLayout from "../components/AppLayout.vue"
import { ref, computed, onMounted, reactive, watch } from "vue"
import * as L from 'leaflet'
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet"
import "leaflet/dist/leaflet.css"
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedReport = ref(null)
const API = `${import.meta.env.VITE_API_URL}/api/v1`
const NEIGHBOURHOOD_ID = 1
const userPostcode = ref('')
const userNeighbourhoodId = ref(NEIGHBOURHOOD_ID)

const zoom = ref(9)
const center = ref([52.4862, -1.8904])
const reports = ref([])

const searchTerm = ref('')
const filterType = ref('')
const sortBy = ref('votes')

const showReportModal = ref(false)
const isSubmitting = ref(false)

const newReport = ref({
    type: '',
    customType: '',
    severity: '',
    title: '',
    description: '', 
    postcode: ''
})

const areaCoordinates = {
    Greater_London: [51.5074, -0.1278],
    Birmingham: [52.4862, -1.8904],
    Manchester: [53.4808, -2.2426]
}

function formatArea(area) {
    if (!area) return 'Unknown area'
    return area.replace(/_/g, ' ')
}
const formIsValid = computed(() => {
    const hasType = newReport.value.type && 
                    (newReport.value.type !== 'Other' || newReport.value.customType.trim())
    return (
        hasType &&
        newReport.value.severity &&
        newReport.value.title.trim() &&
        newReport.value.postcode?.trim().length >= 3
    )
})

function openFullDiscussion(report) {
    selectedReport.value = null
    router.push(`/reports/${report.reportId || report.id}`)
}

async function fetchReports() {
    try {
        const res = await fetch(`${API}/reports/overview?neighbourhoodId=${NEIGHBOURHOOD_ID}`, {
            credentials: 'include'
        })

        if (!res.ok) throw new Error('Failed to fetch overview')

        const apiReports = await res.json()
        console.log('API reports:', apiReports)
        reports.value = apiReports.map(report => {
            const fallback = areaCoordinates[report.area] || null

            return {
                ...report,
                lat: report.lat != null
                    ? Number(report.lat)
                    : fallback
                        ? fallback[0]
                        : null,
                lng: report.lng != null
                    ? Number(report.lng)
                    : fallback
                        ? fallback[1]
                        : null
            }
        })

        console.log(`Loaded ${apiReports.length} reports from /overview`)
        return
    } catch (err) {
        console.warn('Backend not responding, using demo data →', err.message)
        generateReports()
    }
}

async function upvote(report) {
    const id = report.reportId || report.id
    if (!id) return
    try {
        const res = await fetch(`${API}/reports/upvote`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reportId: id })
        })

        if (res.ok) {
            report.votes = (report.votes || 0) + 1
        } else if (res.status === 401) {
            alert('Please log in to vote')
        }
    } catch (err) {
        console.error('Upvote failed', err)
    }
}

async function removeUpvote(report) {
    const id = report.reportId || report.id
    if (!id) return
    try {
        const res = await fetch(`${API}/reports/upvote/remove`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reportId: id })
        })

        if (res.ok && (report.votes || 0) > 0) {
            report.votes--
        } else if (res.status === 401) {
            alert('Please log in to vote')
        }
    } catch (err) {
        console.error('Remove vote failed', err)
    }
}

async function createReport() {
    if (!formIsValid.value) return

    isSubmitting.value = true

    const finalType =
        newReport.value.type === 'Other'
            ? (newReport.value.customType.trim() || 'Other')
            : newReport.value.type

    const payload = {
        neighbourhoodId: NEIGHBOURHOOD_ID,
        title: newReport.value.title.trim(),
        description: newReport.value.description.trim(),
        severity: newReport.value.severity,
        type: finalType, 
        postcode: newReport.value.postcode.trim()
    }

    console.log('Sending report payload:', payload)

    try {
        const res = await fetch(`${API}/reports/create`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })

        const data = await res.json().catch(() => ({}))
        console.log('Create report response:', res.status, data)

        if (res.ok) {
            alert('Report submitted successfully!')
            showReportModal.value = false
            newReport.value = {
                type: '',
                customType: '',
                severity: '',
                title: '',
                description: ''
            }
            await fetchReports()
        } else if (res.status === 401) {
            alert('Please log in to report an issue')
        } else {
            alert(data.message || `Failed to submit report (${res.status})`)
        }
    } catch (err) {
        console.error('Report creation failed', err)
        alert('Something went wrong. Please try again.')
    } finally {
        isSubmitting.value = false
    }
}

//demo data
const disasterTypes = ['Flood', 'Wildfire', 'Storm Damage', 'Road blocked', 'Power Outage', 'Landslide', 'Infrastructure Damage']
const areas = ['Birmingham', 'Coventry', 'Wolverhampton', 'Dudley','Walsall', 'Solihull', 'Sandwell', 'West Bromwich']

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

function generateReports() {
    reports.value = []
    for (let i = 0; i < 100; i++) {
        const area = areas[Math.floor(Math.random() * areas.length)]
        const [centerLat, centerLng] = areaCenters[area] || [52.4862, -1.8904]
        reports.value.push({
            id: i + 1,
            lat: centerLat + (Math.random() - 0.5) * 0.07,
            lng: centerLng + (Math.random() - 0.5) * 0.07,
            type: disasterTypes[Math.floor(Math.random() * disasterTypes.length)],
            area: area,
            severity: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
            status: ['Pending', 'In Progress', 'Resolved'][Math.floor(Math.random() * 3)],
            votes: Math.floor(Math.random() * 47) + 3,
            timestamp: Date.now() - Math.random() * 1000000000
        })
    }
}

const filteredReports = computed(() => {
    let filtered = [...reports.value]

    if (searchTerm.value.trim()) {
        const term = searchTerm.value.toLowerCase().trim()
        filtered = filtered.filter(report =>
            (report.area?.toLowerCase() || '').includes(term) ||
            (report.type?.toLowerCase() || '').includes(term) ||
            (report.title?.toLowerCase() || '').includes(term)
        )
    }

    if (filterType.value) {
        filtered = filtered.filter(report => report.type === filterType.value)
    }

    if (sortBy.value === 'votes') {
        filtered.sort((a, b) => (b.voteCount || b.votes || 0) - (a.voteCount || a.votes || 0))
    } else if (sortBy.value === 'recent') {
        filtered.sort((a, b) => (new Date(b.createdAt || b.date_submitted) - new Date(a.createdAt || a.date_submitted)))
    }

    return filtered
})

const filteredReportsWithLocation = computed(() => {
    return filteredReports.value.filter(report =>
        typeof report.lat === 'number' &&
        typeof report.lng === 'number' &&
        !isNaN(report.lat) &&
        !isNaN(report.lng)
  )
})

const resolvedReports = computed(() => 
    reports.value.filter(r => r.status === 'Resolved')
)

const iconCache = {}
function getIconColor(type) {
    const isDark = isDarkMode.value;
    const colors = {
        'Flood':                 isDark ? '#44adff' : '#2563eb',
        'Wildfire':              isDark ? '#ff5252' : '#dc2626',
        'Storm Damage':          isDark ? '#b388ff' : '#7c3aed',
        'Road blocked':          isDark ? '#ff9100' : '#ea580c',
        'Power Outage':          isDark ? '#ffff00' : '#ca8a04',
        'Landslide':             isDark ? '#a1887f' : '#92400e',
        'Infrastructure Damage': isDark ? '#26a69a' : '#0f766e',
        'Default':               isDark ? '#94a3b8' : '#4f46e5'
    };
    return colors[type] || colors['Default'];
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

async function loadUserInfo() {
    try {
        const res = await fetch(`${API}/users/me`, { credentials: 'include' })
        if (res.ok) {
            const user = await res.json()
            userPostcode.value = user.postcode || ''
        }
    } catch (err) {
        console.warn("Could not load user info", err)
    }
}

onMounted(() => {
    fetchReports()
    loadUserInfo()
})

function openReportModal() {
    newReport.value = {
        type: '',
        customType: '',
        severity: '',
        title: '',
        description: '',
        postcode: userPostcode.value || ''  
    }
    showReportModal.value = true
}

const isUpHovered = ref(null)
const isDownHovered = ref(null)
const isDarkMode = ref(document.documentElement.classList.contains('dark'))

onMounted(() => {
    const observer = new MutationObserver(() => {
        isDarkMode.value = document.documentElement.classList.contains('dark')
    })
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
    })
})

const getUpvoteSrc = (report) => {
    const isThisOneHovered = isUpHovered.value === report.id
    if (isDarkMode.value) {
        return isThisOneHovered ? '/upvote-dark.svg' : '/dark-upvote.svg'
    }
    return isThisOneHovered ? '/upvote-light.svg' : '/light-upvote.svg'
}

const getDownvoteSrc = (report) => {
    const isThisOneHovered = isDownHovered.value === report.id
    if (isDarkMode.value) {
        return isThisOneHovered ? '/downvote-dark.svg' : '/dark-downvote.svg'
    }
    return isThisOneHovered ? '/downvote-light.svg' : '/light-downvote.svg'
}
</script>

<style scoped>
.report-page {
    width: auto;
    height: auto;
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    background: var(--background);
    padding: 2em 4em;
}

.map-container {
    width: auto;
    height: 25rem;
    margin-bottom: 2em;
}

.leaflet-map {
    border-radius: 10px;
    width: 100%;
    height: 100%;
}

.reports-section {
    max-height: 50rem;
    padding: 0;
    overflow-y: auto;
    background: var(--background);
    border-top: 1px solid var(--on-background);
}

.reports-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 1rem 1rem 1rem 0;
    flex-wrap: wrap;
    gap: 1rem;
}

.reports-header h2 {
    margin: 0;
    color: var(--on-background);
}

.no-reports {
    text-align: center;
    color: var(--on-background);
    font-size: 1.rem;
}

.close-modal {
    position: absolute;
    top: 12px;
    right: 16px;
    font-size: 28px;
    background: none;
    border: none;
    color: #aaa;
    cursor: pointer;
}

.meta-row {
    display: flex;
    gap: 1rem;
    margin: 0;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

p {
    margin: 0;
    margin-bottom: 1rem;
    font-size: 1rem;
    color: var(--on-background);
}

.details-text {
    margin: 0;
}

.badge {
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--background);
}

.severity.low {
    background: var(--low);
    color: var(--on-low);
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.severity.medium { 
    background: var(--medium);
    color: var(--on-medium);
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.severity.high {
    background: var(--high);
    color: var(--on-high);
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.status.pending {
    background: var(--pending); color: var(--on-pending);
}

.status.in-progress {
    background: var(--in-progress); color: var(--on-in-progress);
}

.status.resolved {
    background: var(--resolved); color: var(--on-resolved);
}

.description-block {
    margin: 0;
    padding: 0;
    background: var(--background); 
    border-radius: 10px;
}

.details {
    background: var(--surface);
    border-radius: 10px;
    padding: 1rem;
}

.comments-preview-section { margin-top: 24px; border-top: 1px solid #eee; padding-top: 20px; }
.comment-previews { margin: 12px 0; }
.preview-item { margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #f0f0f0; }
.preview-item strong { color: #333; }
.modal-buttons { margin-top: 16px; text-align: center; }

.btn.view-full {
    background: var(--container);
    color: var(--on-container);
    border: none;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    margin: 0;
    padding: 0.8rem;
}

.controls {
    display: flex;
    gap: 1rem;
    padding: 1px;
    flex-wrap: wrap;
}

.search-input,
.filter-select {
    padding: 10px 14px;
    border: 1px solid var(--outline);
    border-radius: 10px;
    color: var(--on-surface);
    background: var(--surface);
    font-size: 0.8rem;
}

.search-input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--primary);
}

.report-issue-btn {
    background: var(--container);
    color: var(--on-container);
    border: none;
    padding: 0.5rem 1rem;

    border-radius: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    white-space: nowrap;
}

.report-issue-btn:hover {
    filter: brightness(0.75);
    box-shadow: 0 20px 4px rgba(var(--shadow) var(--shadow-alpha));
}

.dark .report-issue-btn:hover {
    filter: brightness(1.25);
    box-shadow: 0 20px 4px rgba(var(--shadow) var(--shadow-alpha));
}

.reports-grid {
    display: grid;
    padding: 0 1rem 0 0;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1rem;
}

.report-card {
    background: var(--background);
    border: 1px solid var(--on-background);
    border-radius: 10px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s;
}

.report-card:hover {
    transform: translateY(-4px);
    filter: brightness(0.85);
    box-shadow: 0 20px 4px rgba(var(--shadow) var(--shadow-alpha));
    border-color: var(--outline);
}

.dark .report-card:hover {
    transform: translateY(-4px);
    filter: brightness(1.25);
    box-shadow: 0 10px 20px rgba(var(--shadow) var(--shadow-alpha));
    border-color: var(--outline);
}

.card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

h4 {
    font-size: 1rem;
    margin: 0;
    margin-bottom: 0.5rem;
    color: var(--on-background);
}

.type-badge {
    padding: 4px 10px;
    border-radius: 9999px;
    color: var(--background);
    font-size: 0.8rem;
    font-weight: 600;
}

.status-badge {
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 600;
}

.type-options {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0;
}

.type-btn {
    padding: 8px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 9999px;
    cursor: pointer;
    font-size: 0.8rem;
    background: var(--surface);
    color: var(--on-surface);
    transition: all 0.15s;
}

.type-btn.selected {
    background: var(--container);
    color: var(--on-conatiner);
    border-color: var(--container);
}

.other-input {
    margin-top: 12px;
}

.other-input input {
    width: 100%;
    padding: 10px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
}

.severity {
    margin: 0;
    padding: 0;
    color: var(--on-background);
}

.severity-options {
    display: flex;
    flex-direction: row;
    gap: 1rem;
    margin: 0;
}

.severity-btn {
    display: flex;
    padding: 0.5rem 1rem;
    border: 1px solid var(--outline);
    border-radius: 10px;
    background: var(--background);
    cursor: pointer;
    font-weight: 500;
    color: var(--on-background);
    margin: 0;
}

.severity-btn.selected {
    border-color: var(--on-container);
    background: var(--container);
    color: var(--on-container);
}

.severity-btn input[type="radio"] {
    accent-color: var(--primary);
}

.status-badge.pending {
    background: var(--pending);
    color: var(--on-pending);
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-badge.in-progress {
    background: var(--in-progress);
    color: var(--on-in-progress);
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-badge.resolved {
    background: var(--resolved);
    color: var(--on-resolved);
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 600;
}

.card-bottom {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    align-items: center;
    margin: 0;
}

.separator {
    width: 100%;
    height: 1px;
    background-color: var(--on-background);
    display: inline-block;
    padding: 0;
    margin: 0;
    margin-bottom: 0.5rem;
}

.vote-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.vote-btn {
    width: 1rem;
    background: none;
    padding: 4px;
    margin: 0;
    border: none;
    cursor: pointer;
    color: var(--surface);
}

.upvote-img, .downvote-img {
    height: 1rem;
    width: auto;
}

.vote-count {
    font-size: 1rem;
    font-weight: 400;
    color: var(--on-background);
}

.timestamp {
    color: var(--on-surface);
    font-size: 1rem;
    display: flex;
}

.resolved-teaser {
    margin-top: 30px;
    padding: 16px;
    background: #f1f5f9;
    border-radius: 8px;
    text-align: center;
    color: #475569;
}

.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    z-index: 1000;
    padding: 3rem;
}

.modal-content {
    background: var(--background);
    border-radius: 10px;
    padding: 3rem;
    width: 40rem;
    height: auto;
    overflow-y: auto;
    box-shadow: 0 1rem 2rem rgba(var(--shadow), var(--shadow-alpha));
    box-sizing: border-box;
    max-height: 85vh;
}

.modal-content h3 {
    margin: 0 0 1rem;
    font-size: 1.5rem;
    color: var(--on-background);
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 1rem;
    font-weight: 500;
    color: var(--on-background);
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid var(--outline);
    border-radius: 10px;
    font-size: 1rem;
    background: var(--background);
    color: var(--on-background);
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--primary);
}

#description {
    resize: vertical;
    width: 100%;
    box-sizing: border-box;
}

.hint {
    display: flex;
    margin: 0;
    margin-top: 0.5rem;
    color: var(--on-background);
    font-size: 0.8rem;
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin: 0;
}

.cancel-btn {
    background: var(--surface);
    color: var(--on-surface);
    border: none;
    padding: 0.8rem;
    border-radius: 10px;
    cursor: pointer;
}

.submit-btn {
    background: var(--container);
    color: var(--on-container);
    border: none;
    padding: 0.8rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
}

.submit-btn:disabled {
    background: var(--outline);
    cursor: not-allowed;
}

.popup-card {
    min-width: 240px;
}
.popup-card h3 { margin: 0 0 10px; color: #1e293b; }
.popup-card p { margin: 6px 0; color: #475569; }
</style>
