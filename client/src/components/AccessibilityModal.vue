<template>
    <div
        v-if="accessibility.isOpen"
        class="accessibility-modal"
        @click.self="closeAccessibility"
    >
        <div class="modal-content">
            <h1>Accessibility Settings</h1>

            <div class="setting">
                <div class="text-size">
                    <label>Text Size</label>
                    <span>{{ accessibility.textSize }}%</span>
                </div>
                <input
                    type="range"
                    v-model="accessibility.textSize"
                    min="50"
                    max="150"
                />
            </div>

            <div class="setting">
                <label>Light / Dark Mode</label>
                <button @click="toggleDarkMode" class="toggle-btn">
                    {{ accessibility.darkMode ? "Dark" : "Light" }} Mode
                </button>
            </div>

            <div class="setting">
            <label>Dyslexic Font</label>
            <button
                @click="accessibility.useDyslexicFont = !accessibility.useDyslexicFont"
                class="toggle-btn"
            >
                {{ accessibility.useDyslexicFont ? "ON" : "OFF" }}
            </button>
            </div>

            <div class="setting">
            <label>Colour-blind Mode</label>
            <select v-model="accessibility.colorMode">
                <option value="normal">Normal</option>
                <option value="deuteranopia">Deuteranopia</option>
                <option value="protanopia">Protanopia</option>
                <option value="tritanopia">Tritanopia</option>
            </select>
            </div>

            <button @click="closeAccessibility" class="close-btn">
            Close & Save
            </button>
        </div>
    </div>
</template>

<script setup>
import { computed } from "vue"
import { useAccessibility } from "../composables/useAccessibility"

const { accessibility, closeAccessibility, toggleDarkMode } = useAccessibility()
</script>

<style scoped>
.accessibility-modal {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99999;
    width: 100vw;
    height: 100vh;
}

.modal-content {
    background: var(--background);
    padding: 32px;
    border-radius: 10px;
    min-width: 30%;
    width: fit;
    height: fit;
    box-shadow: 0 1rem 2rem rgba(var(--shadow), var(--shadow-alpha));
}

.setting {
    margin-bottom: 16px;
}

.setting label {
    display: flex;
    font-size: 1rem;
    color: var(--on-background);
    margin-bottom: 8px;
}

.text-size {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: var(--on-background);
    font-size: 16px;
}

h1 {
    padding: 0;
    margin: 0;
    margin-bottom: 16px;
    font-size: 1.5rem;
    color: var(--on-background);
}

.span {
    font-size: 18px;
}

.toggle-btn,
select,
input[type="range"] {
    width: 100%;
    background: var(--surface);
    font-size: 0.8rem;
}

input[type="range"] {
    accent-color: var(--primary);
    background: transparent;
}

.toggle-btn,
select {
    padding: 12.8px;
    border: 1px solid var(--outline);
    border-radius: 10px;
    background: var(--background);
    color: var(--on-background);
    cursor: pointer;
}

.close-btn {
    width: 100%;
    padding: 14px;
    background: var(--container);
    color: var(--on-container);
    border: none;
    border-radius: 10px;
    font-size: 16px;
    margin-top: 16px;
    font-weight: 600;
    cursor: pointer;
}
</style>
