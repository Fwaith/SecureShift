<template>
    <AppLayout>
        <div class="accessibility-page">
            <h1>Accessibility Settings</h1>

            <div class="setting">
                <label for="textSize">Text Size</label>
                <input
                    id="textSize"
                    type="range"
                    min="80"
                    max="150"
                    v-model="useAccessibility.textSize"
                />
                <span>{{ useAccessibility.textSize }}%</span>
            </div>

            <div class="setting">
                <label for="fontMode">Font Style</label>
                <select id="fontMode" v-model="accessibility.fontMode">
                    <option value="default">Default</option>
                    <option value="dyslexic">Dyslexic-friendly</option>
                </select>
            </div>

            <div class="setting">
                <label for="colorMode">Colour Mode</label>
                <select id="colorMode" v-model="accessibility.colorMode">
                    <option value="normal">Normal</option>
                    <option value="deuteranopia">Deuteranopia</option>
                    <option value="protanopia">Protanopia</option>
                    <option value="tritanopia">Tritanopia</option>
                </select>
            </div>
        </div>
    </AppLayout>
</template>

<script setup>
import AppLayout from "../components/AppLayout.vue"
import { useAccessibility } from "../composables/useAccessibility"

const accessibility = useAccessibility()
</script>

<style scoped>
.accessibility-page {
    max-width: 700px;
    margin: 40px auto;
    padding: 24px;
    background: #f8fafc;
    border-radius: 12px;
}

.setting {
    margin-bottom: 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
</style>
