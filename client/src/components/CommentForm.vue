<template>
    <form @submit.prevent="submitComment" class="comment-form">
        <textarea
            v-model="text"
            :placeholder="placeholder"
            rows="3"
            required
        ></textarea>
        <button type="submit" :disabled="sending || !text.trim()">
            {{ sending ? 'Posting...' : 'Post comment' }}
        </button>
    </form>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
    reportId: Number,
    replyToCommentId: { type: Number, default: null },
    placeholder: { type: String, default: 'Write a comment...' }
})

const emit = defineEmits(['comment-created'])

const text = ref('')
const sending = ref(false)

const API = `${import.meta.env.VITE_API_URL}/api/v1`

async function submitComment() {
    if (!text.value.trim()) return
    sending.value = true

    try {
        const res = await fetch(`${API}/comments`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reportId: props.reportId,
                description: text.value.trim(),
                replyToCommentId: props.replyToCommentId || null
            })
        })

        if (res.ok) {
            text.value = ''
            emit('comment-created')
        } else {
            alert('Could not post comment')
        }
    } catch (err) {
        console.error(err)
        alert('Error posting comment')
    } finally {
        sending.value = false
    }
}
</script>

<style scoped>
.comment-form {
    margin-bottom: 24px;
}
textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    resize: vertical;
}
button {
    margin-top: 8px;
    background: #3b82f6;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
}
button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
</style>
