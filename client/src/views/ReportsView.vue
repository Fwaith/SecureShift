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
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution="&copy; OpenStreetMap contributors"
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

                        <button
                            class="report-issue-btn"
                            @click="showReportModal = true"
                        >
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
                        
                        <div class="vote-section">
                            <button 
                                class="vote-btn upvote-btn"
                                @click.stop="upvote(report)"
                            >
                                Upvote
                            </button>
                            <button 
                                class="vote-btn downvote-btn"
                                @click.stop="removeUpvote(report)"
                            >
                                Downvote
                            </button>
                            <span class="vote-count">{{ report.voteCount || report.votes || 0 }} votes</span>
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
                        <p>{{ selectedReport.description || 'No further details provided.' }}</p>
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
import { ref, computed, onMounted } from "vue"
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
    for (let i = 0; i < 12; i++) {
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
</script>

<style scoped>
.report-page {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--background);
    padding: 2em 4em;
}

.map-container {
    height: 60vh;
    min-height: 400px;
    position: relative;
    margin-bottom: 2em;
}

.leaflet-map {
    display: flex;
    border-radius: 10px;
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

.no-reports {
    text-align: center;
    padding: 60px 20px;
    color: #64748b;
    font-size: 1.1rem;
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
    gap: 10px;
    margin: 12px 0;
    flex-wrap: wrap;
}
.badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    color: white;
}

.severity.low    { background: #84cc16; }
.severity.medium { background: #f59e0b; }
.severity.high   { background: #ef4444; }
.status.pending     { background: #fbbf24; color: #78350f; }
.status.in-progress { background: #60a5fa; }
.status.resolved    { background: #34d399; }
.description-block { margin: 20px 0; padding: 16px; background: #f9fafb; border-radius: 8px; }
.comments-preview-section { margin-top: 24px; border-top: 1px solid #eee; padding-top: 20px; }
.comment-previews { margin: 12px 0; }
.preview-item { margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #f0f0f0; }
.preview-item strong { color: #333; }
.modal-buttons { margin-top: 16px; text-align: center; }

.btn.view-full {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
}

.controls {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.search-input,
.filter-select {
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 0.95rem;
}

.report-issue-btn {
    background: #10b981;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    white-space: nowrap;
}

.report-issue-btn:hover {
    background: #059669;
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
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.15s;
}

.type-btn.selected {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
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

.severity-options {
    display: flex;
    gap: 12px;
    margin: 8px 0;
}

.severity-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-weight: 500;
}

.severity-btn.selected {
    border-color: #3b82f6;
    background: #eff6ff;
    color: #1e40af;
}

.severity-btn input {
    margin: 0;
}

.status-badge.pending     { background: #fbbf24; color: #78350f; }
.status-badge.in-progress { background: #60a5fa; color: white; }
.status-badge.resolved    { background: #34d399; color: white; }

.vote-section {
    margin-top: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.vote-btn {
    color: white;
    border: none;
    padding: 6px 14px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
}

.upvote-btn {
    background: #3b82f6;
}

.downvote-btn {
    background: #ef4444;
}

.vote-count {
    font-weight: 600;
    color: #1e40af;
}

.timestamp {
    color: #64748b;
    font-size: 0.85rem;
    display: block;
    margin-top: 8px;
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
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 12px;
    padding: 24px;
    width: 100%;
    max-width: 500px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-content h3 {
    margin: 0 0 20px;
    color: #1e293b;
}

.form-group {
    margin-bottom: 18px;
}

.form-group label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: #475569;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 1rem;
}

.form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 24px;
}

.cancel-btn {
    background: #e2e8f0;
    color: #475569;
    border: none;
    padding: 10px 18px;
    border-radius: 6px;
    cursor: pointer;
}

.submit-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 18px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
}

.submit-btn:disabled {
    background: #93c5fd;
    cursor: not-allowed;
}

.popup-card {
    min-width: 240px;
}
.popup-card h3 { margin: 0 0 10px; color: #1e293b; }
.popup-card p { margin: 6px 0; color: #475569; }
</style>
