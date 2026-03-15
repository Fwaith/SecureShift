<template>
    <div class="map-page">
        <l-map ref="mapRef" v-model:zoom="zoom" :center="center" class="leaflet-map">
            <l-tile-layer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution="&copy; OpenStreetMap contributors"
            />

            <l-marker 
                :lat-lng="floodLocation"
                @click="zoomToFlood"
            >
                <l-popup>
                    Flood reported
                </l-popup>
            </l-marker>
        </l-map>
    </div>
</template>

<script setup>
import { ref } from "vue"
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet"
import "leaflet/dist/leaflet.css"

const zoom = ref(6)
const center = ref([52.3555, -1.1743]) //uk
const floodLocation = [52.48, -1.89] //birm
const mapRef = ref(null)
const zoomToFlood = () => {
    const map = mapRef.value.leafletObject
    map.flyTo(floodLocation, 13)
}
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
