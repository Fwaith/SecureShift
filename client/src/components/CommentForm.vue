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
    margin-bottom: 1rem;
}

textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid var(--outline);
    border-radius: 8px;
    resize: vertical;
    background: var(--background);
    margin: 0;
    margin-top: 1rem;
    margin-bottom: 1rem;
    color: var(--on-background);
}
button {
    background: var(--container);
    color: var(--on-container);
    border: none;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    padding: 0.8rem;
    margin: 0;
}

button:disabled {
    color: var(--on-surface);
    background: var(--surface);
    cursor: not-allowed;
}
</style>
