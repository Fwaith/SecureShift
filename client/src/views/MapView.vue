<template>
    <div class="map-page">
        <l-map
            v-model:zoom="zoom"
            :center="center"
            class="leaflet-map"
        >
        <l-tile-layer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
        />
        </l-map>
    </div>
</template>

<script setup>
import { ref } from "vue"
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet"
import "leaflet/dist/leaflet.css"

const zoom = ref(7)
const center = ref([52.48, -1.89])
</script>

<style scoped>
.map-page {
    width: 100%;
    height: 100vh;
}

.leaflet-map {
    width: 100%;
    height: 100%;
}
</style>
