<template>
    <div
        v-if="accessibility.isOpen"
        class="accessibility-modal"
        @click.self="closeAccessibility"
    >
        <div class="modal-content">
            <h3>Accessibility Settings</h3>

            <div class="setting">
            <label>Text Size</label>
            <input
                type="range"
                v-model="accessibility.textSize"
                min="80"
                max="150"
            />
            <span>{{ accessibility.textSize }}%</span>
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
import { useAccessibility } from "../composables/useAccessibility"

const { accessibility, closeAccessibility } = useAccessibility()
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
}

.modal-content {
    background: white;
    padding: 32px;
    border-radius: 16px;
    max-width: 420px;
    width: 90%;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.setting {
    margin-bottom: 24px;
}

.setting label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
}

.toggle-btn,
select,
input[type="range"] {
    width: 100%;
}

.toggle-btn,
select {
    padding: 10px 16px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: white;
    cursor: pointer;
}

.close-btn {
    width: 100%;
    padding: 14px;
    background: #1e40af;
    color: white;
    border: none;
    border-radius: 8px;
    margin-top: 16px;
    font-weight: 600;
    cursor: pointer;
}
</style>
