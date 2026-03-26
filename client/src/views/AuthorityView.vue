<template>
    <AppLayout>
        <div class="authority-page">
            <section class="page-header">
                <h1>Authority Level Access</h1>
                <p class="subtitle">Manage authority levels and access permissions</p>
            </section>   

            <section class="authority-grid">

                 <div
                    v-for="authority in authorities"
                    :key="authority.id"
                    class="authority-card"
                >
                    <div class="card-top">
                        <span class="authority-icon">👤</span>
                        <span class="level-badge" :class="`badge-${authority.level}`">{{ levelMeta[authority.level].label }}</span>
                    </div>
                    <h3>{{ authority.name }}</h3>
                    <div class="permissions">
                        <div v-for="perm in levelMeta[authority.level].permissions" :key="perm" class="permission-tag">
                            {{ perm }}
                        </div>
                    </div>
                    <div class="card-actions">
                        <button
                            v-if="authority.level === 'admin'"
                            class="btn-revoke"
                            @click="revoke(authority)"
                        >
                            Revoke
                        </button>
                        <button
                            v-else
                            class="btn-edit"
                            @click="promote(authority)"
                        >
                            Promote
                        </button>
                    </div>
                </div>
            </section>

            <!-- <section class="add-section">
                <h2>Grant Authority Access</h2>
                <div class="form-row">
                    <div class="form-field">
                        <label>Full Name</label>
                        <input v-model="newAuthority.name" type="text" placeholder="e.g. Jane Smith" />
                    </div>
                    <div class="form-field">
                        <label>Role</label>
                        <input v-model="newAuthority.role" type="text" placeholder="e.g. Business Analyst" />
                    </div>
                    <div class="form-field">
                        <label>Access Level</label>
                        <select v-model="newAuthority.level">
                            <option value="" disabled>Select level</option>
                            <option v-for="lvl in accessLevels" :key="lvl.value" :value="lvl.value">{{ lvl.label }}</option>
                        </select>
                    </div>
                </div>
                <button class="btn-grant" @click="grantAccess" :disabled="!canGrant">
                    Grant Access
                </button>
            </section> -->

            <transition name="modal-fade">
                <div v-if="editing" class="modal-overlay" @click.self="editing = null">
                    <div class="modal">
                        <h3>Edit Access — {{ editing.name }}</h3>
                        <div class="form-field">
                            <label>Access Level</label>
                            <select v-model="editing.level">
                                <option v-for="lvl in accessLevels" :key="lvl.value" :value="lvl.value">{{ lvl.label }}</option>
                            </select>
                        </div>
                        <div class="modal-actions">
                            <button class="btn-grant" @click="saveEdit">Save Changes</button>
                            <button class="btn-revoke" @click="editing = null">Cancel</button>
                        </div>
                    </div>
                </div>
            </transition>

        </div>
    </AppLayout>
</template>

<script setup>
import AppLayout from "../components/AppLayout.vue"
import { ref, computed, onMounted } from "vue"
import api from "../services/api"
const accessLevels = [
    { value: "user",  label: "User"  },
    { value: "admin", label: "Admin" }
]
 
const levelMeta = {
    user:  { label: "User",  permissions: ["View Reports", "View Forecasts"] },
    admin:   { label: "Admin",   permissions: ["View Reports", "View Forecasts", "Run Analysis", "Edit Records", "Manage Users"] }
}
 

const authorities = ref([])
 
const newAuthority = ref({ name: "", role: "", level: "" })
const editing      = ref(null)
 
const canGrant = computed(() =>
    newAuthority.value.name.trim() && newAuthority.value.role.trim() && newAuthority.value.level
)

async function loadAuthorities() {
    try {
        const response = await api.get("/users")
        const users = Array.isArray(response.data) ? response.data : []

        authorities.value = users.map((user) => ({
            id: user.id,
            name: user.username,
            level: user.level,
        }))
    } catch (error) {
        console.error("Failed to load users", error)
        authorities.value = []
    }
}

onMounted(() => {
    loadAuthorities()
})

function showApiError(error, fallbackMessage) {
    const errorData = error?.response?.data
    const errorCode = errorData?.error
    const errorMessage = errorData?.message

    if (errorCode || errorMessage) {
        alert(`${errorCode || "ERROR"}: ${errorMessage || fallbackMessage}`)
        return
    }

    alert(fallbackMessage)
}
 
function grantAccess() {
    if (!canGrant.value) return
    authorities.value.push({
        id:    Date.now(),
        name:  newAuthority.value.name.trim(),
        role:  newAuthority.value.role.trim(),
        level: newAuthority.value.level
    })
    newAuthority.value = { name: "", role: "", level: "" }
}
 
async function revoke(authority) {
    try {
        await api.post(`/users/${authority.id}/demote`)
        await loadAuthorities()
    } catch (error) {
        showApiError(error, "Failed to revoke admin access.")
    }
}
 
async function promote(authority) {
    try {
        await api.post(`/users/${authority.id}/promote`)
        await loadAuthorities()
    } catch (error) {
        showApiError(error, "Failed to promote user.")
    }
}
 
function openEdit(authority) {
    editing.value = { ...authority }
}
 
function saveEdit() {
    const idx = authorities.value.findIndex(a => a.id === editing.value.id)
    if (idx !== -1) authorities.value[idx].level = editing.value.level
    editing.value = null
}
</script>

<style scoped>
.authority-page {
    min-height: 80vh;
    padding: 2rem;
    padding-left: 4rem;
    padding-right: 4rem;
    background: var(--background);
    margin: 0 auto;
}

.page-header {
    text-align: center;
    margin-bottom: 1rem;
}

.page-header h1 {
    font-size: 1.5rem;
    font-weight: 600 
}

h1 {
    margin: 0;
    font-size: 1.5rem;
    color: var(--on-background);
    margin-bottom: 0.5rem;
}

.subtitle {
    color: var(--on-background);
    font-size: 1rem;
    margin: 0;
}

.authority-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
}
 
.authority-card {
    background: var(--background);
    border: 1px solid var(--on-background);
    border-radius: 10px;
    padding: 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.authority-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.07);
}
 
.card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
 
.authority-icon { font-size: 1.8rem; }
 
.level-badge {
    font-size: 1rem; 
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
}
.badge-viewer  { background: #e0f2fe; color: #0369a1; }
.badge-analyst { background: #fef9c3; color: #854d0e; }
.badge-editor  { background: #ede9fe; color: #6d28d9; }
.badge-user    { background: #e2e8f0; color: #334155; }
.badge-admin   { background: #fee2e2; color: #b91c1c; }
 
.authority-card h3 {
    font-size: 1rem;
    font-weight: 700;
    margin: 0;
    margin-bottom: 0.5rem;
    color: var(--on-background);
}
 
.authority-role {
    font-size: 0.8rem;
    color: #64748b;
    margin: 0 0 14px;
}
 
.permissions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}
 
.permission-tag {
    font-size: 0.75rem;
    background: var(--surface);
    color: var(--on-surface);
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid var(--outline);
}
 
.card-actions {
    display: flex;
    gap: 8px;
}
 
.add-section {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 40px;
}
 
.add-section h2 {
    font-weight: 700;
    margin: 0 0 20px;
    color: #0f172a;
}
 
.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}
 
.form-field {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
 
.form-field label {
    font-weight: 600;
    color: #374151;
}
 
.form-field input,
.form-field select {
    padding: 10px 12px;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    background: #fff;
    color: #0f172a;
    transition: border-color 0.2s;
}
.form-field input:focus,
.form-field select:focus {
    outline: none;
    border-color: #0f172a;
}
 

.btn-grant {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0f172a;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 11px 22px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s, opacity 0.2s;
}
.btn-grant:hover:not(:disabled) { background: #1e293b; }
.btn-grant:disabled { opacity: 0.35; cursor: not-allowed; }
 
.btn-edit {
    flex: 1;
    background: #f1f5f9;
    color: #374151;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}
.btn-edit:hover { background: #e2e8f0; }
 
.btn-revoke {
    flex: 1;
    background: #fff1f2;
    color: #b91c1c;
    border: 1.5px solid #fca5a5;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}
.btn-revoke:hover { background: #fee2e2; }
 

.modal-fade-enter-active { transition: opacity 0.2s; }
.modal-fade-enter-from   { opacity: 0; }
 
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(177, 168, 168, 0.516);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}
 
.modal {
    background: #ffffff;
    border-radius: 16px;
    padding: 32px;
    min-width: 360px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
 
.modal h3 {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0 0 20px;
    color: #0f172a;
}   
 
.modal-actions {
    display: flex;   
    gap: 10px;
    margin-top: 20px;
}         

</style>
