<template>
    <div class="comment-thread">
        <div class="comment-box">
            <div class="comment-header">
                <strong>{{ comment.username }}</strong>
                <span class="date">{{ formatDate(comment.createdAt) }}</span>
            </div>
            <p class="comment-text">{{ comment.description }}</p>

            <button
                v-if="isAuthenticated"
                class="reply-link"
                @click="showReply = !showReply"
            >
                Reply
            </button>
        </div>

        <CommentForm
            v-if="showReply && isAuthenticated"
            :report-id="reportId"
            :reply-to-comment-id="comment.commentId"
            placeholder="Write your reply..."
            @comment-created="onReplyPosted"
        />

        <div v-if="comment.comments?.length" class="replies">
            <CommentThread
                v-for="reply in comment.comments"
                :key="reply.commentId"
                :comment="reply"
                :report-id="reportId"
                :is-authenticated="isAuthenticated"
                @comment-created="$emit('comment-created')"
            />
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import CommentForm from './CommentForm.vue'

const props = defineProps({
    comment: Object,
    reportId: Number,
    isAuthenticated: Boolean
})

const emit = defineEmits(['comment-created'])

const showReply = ref(false)

function formatDate(ts) {
    const timestamp = typeof ts === 'number' 
        ? (ts > 1e10 ? ts : ts * 1000)  
        : ts;
    const date = new Date(timestamp);
    return date.toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
  });
}

function onReplyPosted() {
    showReply.value = false
    emit('comment-created')
}
</script>

<style scope>
.comment-thread { margin-bottom: 20px; }

.comment-box {
    background: #f8fafc;
    padding: 14px 16px;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
}

.comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    color: #1e293b;
}

.date { font-size: 0.82rem; color: #6b7280; }
.comment-text { margin: 0 0 10px; line-height: 1.5; }

.reply-link {
    background: none;
    border: none;
    color: #3b82f6;
    font-size: 0.9rem;
    cursor: pointer;
}

.replies {
    margin-left: 32px;
    margin-top: 12px;
    padding-left: 16px;
    border-left: 2px solid #e5e7eb;
}
</style>
 