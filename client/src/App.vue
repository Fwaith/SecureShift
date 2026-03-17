<script setup>
import { useAccessibility } from "./composables/useAccessibility"

const { appStyle, appClasses } = useAccessibility()
</script>

<template>
    <div :class="appClasses" :style="appStyle" class="app-root">
        <router-view />
    </div>
</template>

<style>
html, body, #app {
    margin: 0;
    padding: 0;
    min-height: 100%;
}

.app-root {
    min-height: 100vh;
}

.color-normal {
    background: #ffffff;
    color: #111827;
}

.color-deuteranopia {
    filter: hue-rotate(20deg);
}

.color-protanopia {
    filter: hue-rotate(40deg);
}

.color-tritanopia {
    filter: hue-rotate(80deg);
}
</style>
