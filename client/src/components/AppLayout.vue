<template>
    <div class="app-shell">
        <AppHeader />

        <main class="page-content">
            <slot />
        </main>

        <AppFooter />
        <AccessibilityModal />
    </div>
</template>

<script setup>
import AppHeader from "./AppHeader.vue"
import AppFooter from "./AppFooter.vue"
import AccessibilityModal from "./AccessibilityModal.vue";
</script>

<style scoped>
.app-shell {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.page-content {
    flex: 1;
}
</style>
