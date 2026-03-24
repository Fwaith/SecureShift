<template>
    <AppLayout>
        <div class="authority-page">
            <section class="page-header">
                <h1>Forecast Analyser</h1>
                <p class="subtitle">Enter current conditions to assess environmental danger levels:</p>
            </section>

            <section class="forecast-form">
                <div class="fields-grid"> 

                    <div
                        v-for="field in fields"
                        :key="field.id"
                        class="field-card"
                        :class="{ 'field-focused': focusedField === field.id }"
                    >
                        <div class="field-icon">{{ field.icon }}</div>
                        <label :for="field.id">
                            {{ field.label }}
                            <span class="unit-badge">{{ field.unit }}</span>
                        </label>
                        <input
                            :id="field.id"
                            v-model.number="formData[field.id]"
                            type="number"
                            :min="field.min"
                            :max="field.max"
                            :step="field.step"
                            :placeholder="field.placeholder"
                            :required="field.required"
                            @focus="focusedField = field.id"
                            @blur="focusedField = null"
                        />
                        <div v-if="errors[field.id]" class="field-error"> {{ errors[field.id] }}</div>
                        <div class="field-range">{{ field.min }}{{ field.unit }} - {{ field.max }}{{ field.unit }}</div>
                    </div>
                </div>
 
                <div class="actions">
                    <button class="btn-analyse" @click="analyse" :disabled="!isFormComplete">
                        Analyse Conditions
                    </button>
                    <button class="btn-reset" @click="reset">Reset</button>
                </div>
            </section>
 
            
            <transition name="result-slide">
                <section v-if="result" class="result-panel" :class="`result-${result.level}`">
 
                    <div class="result-header">
                        <div class="traffic-lights">
                            <div class="light red"   :class="{ active: result.level === 'danger' }"></div>
                            <div class="light amber" :class="{ active: result.level === 'amber'  }"></div>
                            <div class="light green" :class="{ active: result.level === 'safe'   }"></div>
                        </div>
                        <div class="result-summary">
                            <span class="result-badge" :style="{ backgroundColor: riskConfig.color }">
                                {{ riskConfig.label }}
                            </span>
                            <p class="result-description">{{ riskConfig.description }}</p>
                        </div>
                    </div>
 
                    <div class="result-breakdown">
                        <h3>Field Breakdown</h3>
                        <div class="breakdown-grid">
                            <div
                                v-for="item in breakdown"
                                :key="item.id"
                                class="breakdown-item"
                            >
                                <span class="breakdown-icon">{{ item.icon }}</span>
                                <div class="breakdown-info">
                                    <span class="breakdown-label">{{ item.label }}</span>
                                    <span class="breakdown-value">{{ item.value }}{{ item.unit }}</span>
                                    <span class="breakdown-note">{{ item.note }}</span>
                                </div>
                                <div class="breakdown-indicator" :class="`ind-${item.level}`"></div>
                            </div>
                        </div>
                    </div>
 
                    <div class="result-advice">
                        <span class="advice-icon"></span> 
                        {{ riskConfig.advice }}  
                    </div>
 
                </section>
            </transition>    
        </div>
    </AppLayout>
</template>

<script setup>
import AppLayout from "../components/AppLayout.vue"
import { ref, computed } from "vue"


const fields = [
    {
        id: "temperature",
        label: "Temperature",
        unit: "°C",
        min: -30,
        max: 60,
        step: 0.1,
        placeholder: "e.g. 24.5",
    },
    {
        id: "rainfall",
        label: "Rainfall",
        unit: "mm/hr",
        min: 0,
        max: 300,
        step: 0.1,
        placeholder: "e.g. 12.0",
    },
    {
        id: "humidity",
        label: "Humidity",
        unit: "%",
        min: 0,
        max: 100,
        step: 1,
        placeholder: "e.g. 75",
    }
]
 
const thresholds = {
    temperature: {
        safe:   { min: 5,  max: 28, label: "Normal range"},
        amber:  { min: -5, max: 38, label: "Slight concern"},
        danger: {                   label: "Extreme temperature"}
    },
    rainfall: {
        safe:   { min: 0,  max: 10,  label: "Light rain"},
        amber:  { min: 10, max: 50,  label: "Moderate rainfall"},
        danger: {                    label: "Extreme rainfall"}
    },
    humidity: {
        safe:   { min: 30, max: 65, label: "Comfortable"},
        amber:  { min: 15, max: 85, label: "Uncomfortable range"},
        danger: {                   label: "Dangerous humidity"}
    }
}
 
/*test */

const riskLevels = {
    safe: {
        color: "#22c55e",
        label: "Safe",
        description: "Conditions are within normal environmental parameters. No immediate risk detected.",
        advice: "Conditions are suitable for outdoor activities. Stay observant of any changes."
    },
    amber: {
        color: "#f59e0b",
        label: "Caution",
        description: "One or more readings are outside the ideal range. Exercise caution.",
        advice: "Monitor conditions closely. Limit prolonged outdoor exposure and stay informed."
    },
    danger: {
        color: "#ef4444",
        label: "Danger",
        description: "Conditions indicate significant environmental risk. Immediate action is necessary.",
        advice: "Avoid unnecessary outdoor exposure. Follow local authority guidlines and remain safe."
    }
}
 
const formData      = ref({})
const result       = ref(null)
const focusedField = ref(null)
const errors       = ref({})
 
const isFormComplete = computed(() =>
    fields.every(f => formData.value[f.id] !== undefined && formData.value[f.id] !== "")
)
 

function getRiskLevel(fieldId, value) {
    const t = thresholds[fieldId]
    if (!t) return "safe"
    if (value >= t.safe.min  && value <= t.safe.max)  return "safe"
    if (value >= t.amber.min && value <= t.amber.max) return "amber"
    return "danger"
}
 
const levelOrder = { safe: 0, amber: 1, danger: 2 }
 
function analyse() {
    if (!isFormComplete.value) return

    errors.value = {}
    let hasErrors = false
    fields.forEach(field => {
        const value = formData.value[field.id]
        if (value < field.min || value > field.max) {
            errors.value[field.id] = `Must be between ${field.min}${field.unit} and ${field.max}${field.unit}`
            hasErrors = true
        }
    })
    if (hasErrors) return
 
    const fieldResults = fields.map(field => {
        const value = formData.value[field.id]
        const level = getRiskLevel(field.id, value)
        const note  = thresholds[field.id][level]?.label ?? ""
        return { id: field.id, label: field.label, icon: field.icon, unit: field.unit, value, level, note }
    })
 
    const worstLevel = fieldResults.reduce(
        (worst, item) => levelOrder[item.level] > levelOrder[worst] ? item.level : worst,
        "safe"
    )
 
    result.value = { level: worstLevel, fields: fieldResults }
}
 
const breakdown  = computed(() => result.value?.fields ?? [])
const riskConfig = computed(() => result.value ? riskLevels[result.value.level] : null)
 
function reset() {
    formData.value = {}
    result.value   = null
    errors.value   = {}
}

</script>

<style scoped> 

.page-container {
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 30px;
    text-align: center;
}

.page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.fields-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin-bottom: 28px;
    padding: 0 20px;
}
 
.field-card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
 
.field-card.field-focused {
    border-color: #0f172a;
    box-shadow: 0 0 0 4px rgba(15, 23, 42, 0.06);
    transform: translateY(-2px);
}

 
label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 10px;
}

 
input[type="number"] {
    width: 100%;
    padding: 10px 12px;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
   
}
input[type="number"]::-webkit-inner-spin-button { -webkit-appearance: none; }
input[type="number"]:focus {
    outline: none;
    border-color: #0f172a;
}

 

.actions {
    display: flex;
    align-items: center;
    gap: 12px;
}
 
.btn-analyse {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #0f172a;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 13px 26px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s, transform 0.15s, opacity 0.2s;
}

.btn-analyse:hover:not(:disabled) { background: #1e293b; transform: translateY(-1px); }
.btn-analyse:disabled { opacity: 0.2; cursor: not-allowed; }
 
.btn-reset {
    background: transparent;
    border: 1.0px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 20px;
    color: #64748b;
    cursor: pointer;
    transition: border-color 0.2s, color 0.2s;
}
.btn-reset:hover { border-color: #94a3b8; color: #374151; }
 
.result-slide-enter-active { transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.result-slide-enter-from   { opacity: 0; transform: translateY(20px); }
 
.result-panel {
    margin-top: 36px;
    border-radius: 16px;
    padding: 28px;
    border: 2px solid transparent;
}
 
.result-safe   { background: #f0fdf4; border-color: #86efac; }
.result-amber  { background: #fffbeb; border-color: #fcd34d; }
.result-danger { background: #fff1f2; border-color: #fca5a5; }
 
.result-header {
    display: flex;
    align-items: flex-start;
    gap: 22px;
    margin-bottom: 24px;
}
 
.traffic-lights {
    display: flex;
    flex-direction: column;
    gap: 6px;
    background: #1e293b;
    padding: 10px 9px;
    border-radius: 40px;
    flex-shrink: 0;
}
 
.light {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    transition: opacity 0.3s, box-shadow 0.3s;
}
.light.red   { background: #ef4444; opacity: 0.2; }
.light.amber { background: #f59e0b; opacity: 0.2; }
.light.green { background: #22c55e; opacity: 0.2; }
.light.red.active   { opacity: 1; box-shadow: 0 0 10px rgba(239, 68,  68,  0.6); }
.light.amber.active { opacity: 1; box-shadow: 0 0 10px rgba(245, 158, 11,  0.6); }
.light.green.active { opacity: 1; box-shadow: 0 0 10px rgba(34,  197, 94,  0.6); }
 
.result-badge {
    display: inline-block;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 8px;
}
 
.result-description {
    font-size: 0.95rem;
    color: #374151;
    margin: 0;
    line-height: 1.55;
}
  
.breakdown-grid { display: flex; flex-direction: column; gap: 8px; }
 
.breakdown-item {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 10px;
    padding: 10px 14px;
}
 
.breakdown-icon { font-size: 1.1rem; }
 
.breakdown-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
 
.breakdown-label { font-size: 0.85rem; font-weight: 600; color: #374151; }
.breakdown-value {font-size: 0.85rem; color: #0f172a; }
.breakdown-note  { font-size: 0.75rem; color: #64748b; font-style: italic; }
 
.breakdown-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.ind-safe   { background: #22c55e; box-shadow: 0 0 6px rgba(34,  197, 94,  0.5); }
.ind-amber  { background: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11,  0.5); }
.ind-danger { background: #ef4444; box-shadow: 0 0 6px rgba(239, 68,  68,  0.5); }
 
.result-advice {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-top: 18px;
    padding-top: 18px;
    border-top: 1px solid rgba(0, 0, 0, 0.07);
    font-size: 1.25rem;
    color: #374151;
    line-height: 1.5;
}

</style> 