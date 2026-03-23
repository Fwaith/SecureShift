<template>
    <AppLayout>
        <div class="detail-container">
            <button class="back-button" @click="$router.back()">← Back to reports</button>

            <div v-if="report" class="report-detail">
                <h1>{{ report.title || report.type }}</h1>

                <div class="meta">
                    <span class="badge" :style="{ backgroundColor: getIconColor(report.type) }">{{ report.type }}</span>
                    <span class="badge" :class="report.severity?.toLowerCase()">Severity: {{ report.severity }}</span>
                    <span class="badge" :class="report.status?.toLowerCase()">Status: {{ report.status }}</span>
                    <span>Votes: {{ report.voteCount || 0 }}</span>
                </div>

                <div class="description">
                    <h3>Description</h3>
                    <p>{{ report.description || 'No description provided.' }}</p>
                </div>

                <div class="comments-area">
                    <h2>Discussion ({{ totalCommentCount }})</h2>

                    <CommentForm
                        v-if="isAuthenticated"
                        :report-id="reportId"
                        @comment-created="loadReport"
                        placeholder="Write your comment..."
                    />

                    <div v-if="sortedTopLevelComments.length" class="comment-list">
                        <CommentThread
                            v-for="comment in displayedComments"
                            :key="comment.commentId"
                            :comment="comment"
                            :report-id="reportId"
                            :is-authenticated="isAuthenticated"
                            @comment-created="loadReport"
                        />
                    </div>

                    <p v-else class="empty-state"> No comments yet. {{ isAuthenticated ? 'Be the first!' : 'Log in to comment.' }}</p>
        
                    <div v-if="sortedTopLevelComments.length > 2 && !showAllComments" class="view-all-teaser">
                        <button @click="showAllComments = true" class="view-all-btn">
                            View all {{ totalCommentCount }} comments
                        </button>
                    </div>
                </div>
            </div>

            <div v-else-if="loading" class="loading">Loading report...</div>
            <div v-else class="not-found">Report not found.</div>
        </div>
    </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from "../components/AppLayout.vue"
import CommentForm from '../components/CommentForm.vue'
import CommentThread from '../components/CommentThread.vue'

const route = useRoute()
const reportId = Number(route.params.reportId)

const report = ref(null)
const loading = ref(true)
const isAuthenticated = ref(false)
const showAllComments = ref(false)

const API_BASE = `${import.meta.env.VITE_API_URL}/api/v1`

async function loadReport() {
    loading.value = true
    try {
        const res = await fetch(`${API_BASE}/reports/${reportId}`, { credentials: 'include' })
        if (res.ok) {
            report.value = await res.json()
        }
    } catch (err) {
        console.error(err)
    } finally {
        loading.value = false
    }
}

onMounted(async () => {
    await loadReport()
    const me = await fetch(`${API_BASE}/users/me`, { credentials: 'include' })
    isAuthenticated.value = me.ok
})

const totalCommentCount = computed(() => {
    if (!report.value?.comments?.length) return 0

    function countAll(comments) {
        let total = comments.length
        for (const c of comments) {
            if (c.comments?.length) {
                total += countAll(c.comments)
            }
        }
        return total
    }

    return countAll(report.value.comments)
})

const sortedTopLevelComments = computed(() => {
    if (!report.value?.comments?.length) return []
    return [...report.value.comments].sort((a, b) => {
        return new Date(b.createdAt) - new Date(a.createdAt)
    })
})

const displayedComments = computed(() => {
    if (showAllComments.value) {
        return sortedTopLevelComments.value
    }
    return sortedTopLevelComments.value.slice(0, 2)
})

function getIconColor(type) {
    const colors = {
        'Flood': '#2563eb',
        'Wildfire': '#dc2626',
        'Storm Damage': '#7c3aed',
        'Road blocked': '#ea580c',
        'Power Outage': '#ca8a04',
        'Landslide': '#92400e',
        'Infrastructure Damage': '#0f766e'
    }
    return colors[type] || '#6b7280'
}
</script>

<style scoped>
.detail-container { max-width: 900px; margin: 32px auto; padding: 0 16px; }
.back-button { background: none; border: none; color: #3b82f6; font-weight: 600; margin-bottom: 16px; cursor: pointer; }
.report-detail { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.meta { display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0; color: #64748b; }
.badge { padding: 6px 12px; border-radius: 999px; font-size: 0.9rem; font-weight: 500; }
.description { margin: 24px 0; line-height: 1.6; }
.comments-area { margin-top: 32px; }
.comment-list { margin-top: 16px; }
.empty-state { color: #6b7280; text-align: center; padding: 40px 0; }

.view-all-teaser {
    margin-top: 24px;
    text-align: center;
}

.view-all-btn {
    background: #f1f5f9;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    color: #3b82f6;
    font-weight: 600;
    cursor: pointer;
    font-size: 1rem;
}

.view-all-btn:hover {
    background: #e2e8f0;
}
</style>
