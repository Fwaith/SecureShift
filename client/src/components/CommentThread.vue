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
.comment-thread {
    margin-bottom: 1rem;
}

.comment-box {
    background: var(--background);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid var(--outline);
    border-left: 4px solid var(--primary);
}

.comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    color: var(--on-background);
    font-size: 1rem;
}

.date {
    font-size: 0.80rem;
    color: var(--outline);
}

.comment-text {
    margin: 0 0 10px;
    line-height: 1.5;
    font-size: 0.8rem;
    color: var(--on-background);
}

.reply-link {
    background: none;
    border: none;
    color: var(--primary);
    font-size: 0.8rem;
    cursor: pointer;
}

.replies {
    margin-left: 32px;
    margin-top: 12px;
    padding-left: 16px;
    border-left: 2px solid ;
}
</style>
